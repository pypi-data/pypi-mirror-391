import av
import numba


@numba.jit(
    (
        numba.types.MemoryView(numba.uint8, 1, "C"),
        numba.types.MemoryView(numba.uint8, 1, "C"),
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
    ),
    nopython=True,
    nogil=True,
)
def _frame_paste_rgba(
    dst_view: memoryview,
    src_view: memoryview,
    x: int,
    y: int,
    dw: int,
    dh: int,
    sw: int,
    sh: int,
    src_stride: int,
    dst_stride: int,
):
    sx = sy = 0

    if x < 0:
        sx -= x
        sw += x
        x = 0
    if y < 0:
        sy -= y
        sh += y
        y = 0

    sw = min(sw, sw - sx, dw - x)
    sh = min(sh, sh - sy, dh - y)

    if sw <= 0 or sh <= 0:
        return

    s_base = sy * src_stride + sx * 4
    d_base = y * dst_stride + x * 4
    row_bytes = sw * 4

    for r in range(sh):
        so = s_base + r * src_stride
        do = d_base + r * dst_stride
        dst_view[do : do + row_bytes] = src_view[so : so + row_bytes]


def frame_paste_rgba(dst: av.VideoFrame, src: av.VideoFrame, x: int, y: int):
    assert src.format.name == "rgba" and dst.format.name == "rgba"

    dst.make_writable()

    src_plane = src.planes[0]
    dst_plane = dst.planes[0]

    _frame_paste_rgba(
        memoryview(dst_plane),
        memoryview(src_plane),
        x,
        y,
        dst.width,
        dst.height,
        src.width,
        src.height,
        src_plane.line_size,
        dst_plane.line_size,
    )
    return dst


@numba.jit(
    (
        numba.types.MemoryView(numba.uint8, 1, "C"),
        numba.types.MemoryView(numba.uint8, 1, "C"),
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
    ),
    nopython=True,
    nogil=True,
)
def _blit_8bit_planar(
    dst_view: memoryview,
    src_view: memoryview,
    dx: int,
    dy: int,
    sx: int,
    sy: int,
    w: int,
    h: int,
    dst_stride: int,
    src_stride: int,
):
    if w <= 0 or h <= 0:
        return
    row_bytes = w  # 1 byte per pixel in 8-bit planar
    s_base = sy * src_stride + sx
    d_base = dy * dst_stride + dx
    for r in range(h):
        so = s_base + r * src_stride
        do = d_base + r * dst_stride
        dst_view[do : do + row_bytes] = src_view[so : so + row_bytes]


@numba.jit(
    (
        numba.types.MemoryView(numba.uint8, 1, "C"),
        numba.types.MemoryView(numba.uint8, 1, "C"),
        numba.types.MemoryView(numba.uint8, 1, "C"),
        numba.types.MemoryView(numba.uint8, 1, "C"),
        numba.types.MemoryView(numba.uint8, 1, "C"),
        numba.types.MemoryView(numba.uint8, 1, "C"),
        numba.types.MemoryView(numba.uint8, 1, "C"),
        numba.types.MemoryView(numba.uint8, 1, "C"),
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
        numba.int64,
    ),
    nopython=True,
    nogil=True,
)
def _frame_paste_yuva420p(
    dst_view_y: memoryview,
    dst_view_u: memoryview,
    dst_view_v: memoryview,
    dst_view_a: memoryview,
    src_view_y: memoryview,
    src_view_u: memoryview,
    src_view_v: memoryview,
    src_view_a: memoryview,
    x: int,
    y: int,
    dw: int,
    dh: int,
    sw: int,
    sh: int,
    src_stride_y: int,
    src_stride_u: int,
    src_stride_v: int,
    src_stride_a: int,
    dst_stride_y: int,
    dst_stride_u: int,
    dst_stride_v: int,
    dst_stride_a: int,
):
    sw0, sh0 = sw, sh
    dw, dh = dw, dh

    sx = max(0, -x)
    sy = max(0, -y)
    dx = max(0, x)
    dy = max(0, y)

    w = min(sw0 - sx, dw - dx)
    h = min(sh0 - sy, dh - dy)

    if w <= 0 or h <= 0:
        return

    _blit_8bit_planar(
        dst_view_y,
        src_view_y,
        dx,
        dy,
        sx,
        sy,
        w,
        h,
        dst_stride_y,
        src_stride_y,
    )

    _blit_8bit_planar(
        dst_view_a,
        src_view_a,
        dx,
        dy,
        sx,
        sy,
        w,
        h,
        dst_stride_a,
        src_stride_a,
    )

    hsub = 1
    vsub = 1

    sx_c = sx >> hsub
    sy_c = sy >> vsub
    dx_c = dx >> hsub
    dy_c = dy >> vsub

    src_cw = (sw0 + (1 << hsub) - 1) >> hsub
    src_ch = (sh0 + (1 << vsub) - 1) >> vsub
    dst_cw = (dw + (1 << hsub) - 1) >> hsub
    dst_ch = (dh + (1 << vsub) - 1) >> vsub

    w_c = ((sx + w + (1 << hsub) - 1) >> hsub) - (sx >> hsub)
    h_c = ((sy + h + (1 << vsub) - 1) >> vsub) - (sy >> vsub)

    w_c = min(w_c, src_cw - sx_c, dst_cw - dx_c)
    h_c = min(h_c, src_ch - sy_c, dst_ch - dy_c)

    if w_c > 0 and h_c > 0:
        _blit_8bit_planar(
            dst_view_u,
            src_view_u,
            dx_c,
            dy_c,
            sx_c,
            sy_c,
            w_c,
            h_c,
            dst_stride_u,
            src_stride_u,
        )
        _blit_8bit_planar(
            dst_view_v,
            src_view_v,
            dx_c,
            dy_c,
            sx_c,
            sy_c,
            w_c,
            h_c,
            dst_stride_v,
            src_stride_v,
        )


def frame_paste_yuva420p(dst: av.VideoFrame, src: av.VideoFrame, x: int, y: int):
    assert src.format.name == "yuva420p" and dst.format.name == "yuva420p"

    dst.make_writable()

    src_Y, src_U, src_V, src_A = src.planes
    dst_Y, dst_U, dst_V, dst_A = dst.planes

    _frame_paste_yuva420p(
        memoryview(dst_Y),
        memoryview(dst_U),
        memoryview(dst_V),
        memoryview(dst_A),
        memoryview(src_Y),
        memoryview(src_U),
        memoryview(src_V),
        memoryview(src_A),
        x,
        y,
        dst.width,
        dst.height,
        src.width,
        src.height,
        src_Y.line_size,
        src_U.line_size,
        src_V.line_size,
        src_A.line_size,
        dst_Y.line_size,
        dst_U.line_size,
        dst_V.line_size,
        dst_A.line_size,
    )

    return dst
