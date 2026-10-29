"""
3D steady-state thermal model of the hot plate (finite volume, Cartesian grid, circular mask).

Purpose: check top-surface temperature uniformity over the 100 mm wafer zone for different heater
layouts, plate sizes and insulation, and find the steady-state heater power at each setpoint.

Simplifications (stated honestly in the README):
 - constant thermal conductivity of 6061 aluminium (k = 170 W/m.K)
 - heaters modelled as volumetric sources in 10 mm wide strips (no cartridge/hole contact resistance)
 - radiation linearised and iterated; ambient 25 C
 - wafer and wafer-to-plate air gap NOT modelled here (handled separately in the design notes)
 - circular plate approximated by a staircase mask; exposed side area corrected by pi/4
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

SIGMA = 5.670374e-8
TA = 25.0


def h_rad(T, eps):
    Tk, Tak = T + 273.15, TA + 273.15
    return SIGMA * eps * (Tk**2 + Tak**2) * (Tk + Tak)


class Plate:
    def __init__(self, R=0.075, t=0.025, dx=0.0025, k=170.0):
        self.R, self.t, self.dx, self.k = R, t, dx, k
        n = int(round(2 * R / dx))
        self.n = n
        xs = (np.arange(n) + 0.5) * dx - R
        self.xs = xs
        self.X, self.Y = np.meshgrid(xs, xs, indexing="ij")
        self.mask = np.hypot(self.X, self.Y) <= R
        self.nz = int(round(t / dx))
        nz = self.nz
        idx = -np.ones((n, n, nz), dtype=int)
        m3 = np.repeat(self.mask[:, :, None], nz, axis=2)
        idx[m3] = np.arange(m3.sum())
        self.idx = idx
        self.N = int(m3.sum())
        Gc = k * dx
        rows, cols = [], []
        for ax in range(3):
            a = [slice(None)] * 3
            b = [slice(None)] * 3
            a[ax] = slice(0, -1)
            b[ax] = slice(1, None)
            ia, ib = idx[tuple(a)], idx[tuple(b)]
            ok = (ia >= 0) & (ib >= 0)
            rows.append(ia[ok]); cols.append(ib[ok])
        r = np.concatenate(rows); c = np.concatenate(cols)
        Cm = sp.coo_matrix((np.full(len(r), -Gc), (r, c)), shape=(self.N, self.N))
        Cm = Cm + Cm.T
        self.Cmat = Cm.tocsr()
        self.base_diag = -np.asarray(self.Cmat.sum(axis=1)).ravel()  # sum of Gc per node
        self.top_idx = idx[:, :, 0][self.mask]
        self.bot_idx = idx[:, :, nz - 1][self.mask]
        faces = np.zeros((n, n), dtype=int)
        for (di, dj) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.zeros_like(self.mask)
            ii = slice(max(di, 0), n + min(di, 0))
            jj = slice(max(dj, 0), n + min(dj, 0))
            i2 = slice(max(-di, 0), n + min(-di, 0))
            j2 = slice(max(-dj, 0), n + min(-dj, 0))
            nb = np.zeros_like(self.mask)
            nb[i2, j2] = self.mask[ii, jj]
            faces += (self.mask & ~nb).astype(int)
        self.side_faces = np.zeros(self.N)
        for iz in range(nz):
            self.side_faces[idx[:, :, iz][self.mask]] = faces[self.mask]

    def source_vector(self, layout, z_depth):
        dx, nz = self.dx, self.nz
        iz = min(max(int(round(z_depth / dx - 0.5)), 0), nz - 1)
        q = np.zeros(self.N)
        weights = []
        for (yc, Lh, w) in layout:
            sel = (np.abs(self.Y - yc) <= 0.005) & (np.abs(self.X) <= Lh / 2) & self.mask
            ids = self.idx[:, :, iz][sel]
            weights.append((ids, w))
        tot = sum(w for _, w in weights)
        for ids, w in weights:
            q[ids] += (w / tot) / len(ids)
        return q  # per-watt distribution

    def solve(self, P, layout, z_depth=0.017, eps_top=0.2, hc_top=8.0, h_side=3.0,
              h_bot=6.0, iters=8, T0=None, P_rim=0.0, rim_layers=None):
        dx = self.dx
        A = dx * dx
        q = P * self.source_vector(layout, z_depth)
        if P_rim:
            w = self.side_faces.copy()
            if rim_layers is not None:   # restrict band heater to the top `rim_layers` cell layers
                keep = np.zeros(self.N)
                for iz in range(rim_layers):
                    keep[self.idx[:, :, iz][self.mask]] = 1.0
                w = w * keep
            q = q + P_rim * w / w.sum()
        T = np.full(self.N, TA) if T0 is None else T0.copy()
        for _ in range(iters):
            diag = self.base_diag.copy()
            rhs = q.copy()
            Tt = T[self.top_idx]
            ht = hc_top + h_rad(Tt, eps_top)
            diag[self.top_idx] += ht * A
            rhs[self.top_idx] += ht * A * TA
            diag[self.bot_idx] += h_bot * A
            rhs[self.bot_idx] += h_bot * A * TA
            gs = h_side * A * self.side_faces * (np.pi / 4.0)
            diag += gs
            rhs += gs * TA
            M = (self.Cmat + sp.diags(diag)).tocsc()
            T = spla.spsolve(M, rhs)
        Tt = T[self.top_idx]
        Qtop = np.sum((hc_top + h_rad(Tt, eps_top)) * (Tt - TA) * A)
        Qbot = np.sum(h_bot * (T[self.bot_idx] - TA) * A)
        Qside = np.sum(h_side * A * self.side_faces * (np.pi / 4.0) * (T - TA))
        return dict(T=T, Qtop=Qtop, Qbot=Qbot, Qside=Qside)

    def top_field(self, T):
        f = np.full((self.n, self.n), np.nan)
        f[self.mask] = T[self.top_idx]
        return f

    def section_field(self, T, iy=None):
        """x-z section through the centre line (y ~ 0)."""
        if iy is None:
            iy = self.n // 2
        out = np.full((self.n, self.nz), np.nan)
        for iz in range(self.nz):
            i = self.idx[:, iy, iz]
            ok = i >= 0
            out[ok, iz] = T[i[ok]]
        return out

    def wafer_stats(self, T, r_wafer=0.05):
        f = self.top_field(T)
        r = np.hypot(self.X, self.Y)
        sel = (r <= r_wafer) & self.mask
        v = f[sel]
        c = f[np.unravel_index(np.argmin(np.where(self.mask, r, 9)), f.shape)]
        return dict(center=float(c), tmin=float(v.min()), tmax=float(v.max()),
                    span=float(v.max() - v.min()), mean=float(v.mean()))

    def power_for_setpoint(self, Tset, layout, rim_frac=0.0, rim_layers=None, **kw):
        # secant on P so that wafer-zone mean top temperature = Tset
        P0, P1 = 50.0, 200.0
        r0 = self.solve(P0*(1-rim_frac), layout, P_rim=P0*rim_frac, rim_layers=rim_layers, **kw); s0 = self.wafer_stats(r0["T"])["mean"]
        r1 = self.solve(P1*(1-rim_frac), layout, P_rim=P1*rim_frac, rim_layers=rim_layers, **kw); s1 = self.wafer_stats(r1["T"])["mean"]
        for _ in range(8):
            P2 = P1 + (Tset - s1) * (P1 - P0) / (s1 - s0)
            P0, s0 = P1, s1
            P1 = P2
            r1 = self.solve(P1*(1-rim_frac), layout, T0=r1["T"], P_rim=P1*rim_frac, rim_layers=rim_layers, **kw)
            s1 = self.wafer_stats(r1["T"])["mean"]
            if abs(s1 - Tset) < 0.01:
                break
        return P1, r1, self.wafer_stats(r1["T"])
