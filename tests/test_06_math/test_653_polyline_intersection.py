#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import (
    intersect_polylines_2d,
    intersect_polylines_3d,
    Vec2,
    Vec3,
    ConstructionEllipse,
    BSpline,
)
from ezdxf.render import forms


class TestIntersectPolylines2d:
    def test_intersecting_single_segments(self):
        pline1 = Vec2.list([(0, 1), (2, 1)])
        pline2 = Vec2.list([(1, 0), (1, 2)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 1
        assert res[0].isclose(Vec2(1, 1))

    def test_none_intersecting_single_segments(self):
        pline1 = Vec2.list([(0, 0), (2, 0)])
        pline2 = Vec2.list([(0, 1), (2, 1)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 0

    def test_intersecting_cross(self):
        pline1 = Vec2.list([(0, 1), (1, 1), (2, 1)])
        pline2 = Vec2.list([(1, 0), (1, 1), (1, 2)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 1
        assert res[0].isclose(Vec2(1, 1))

    def test_intersecting_x_cross(self):
        pline1 = Vec2.list([(0, 0), (1, 1), (2, 2)])
        pline2 = Vec2.list([(2, 0), (1, 1), (0, 2)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 1
        assert res[0].isclose(Vec2(1, 1))

    def test_intersecting_zig_zag_lines(self):
        pline1 = Vec2.list([(0, 0), (2, 2), (4, 0), (6, 2), (8, 0)])
        pline2 = Vec2.list([(0, 2), (2, 0), (4, 2), (6, 0), (8, 2)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 4
        res.sort()  # do not rely on any order
        assert res[0].isclose(Vec2(1, 1))
        assert res[1].isclose(Vec2(3, 1))
        assert res[2].isclose(Vec2(5, 1))
        assert res[3].isclose(Vec2(7, 1))

    def test_zig_zag_lines_with_common_vertices(self):
        pline1 = Vec2.list([(0, 0), (2, 2), (4, 0), (6, 2), (8, 0)])
        pline2 = Vec2.list([(0, 4), (2, 2), (4, 4), (6, 2), (8, 4)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 2
        res.sort()  # do not rely on any order
        assert res[0].isclose(Vec2(2, 2))
        assert res[1].isclose(Vec2(6, 2))

    def test_complex_ellipse_with_spline_intersection(self):
        ellipse = ConstructionEllipse(center=(0, 0), major_axis=(3, 0), ratio=0.5)
        bspline = BSpline([(-4, -4), (-2, -1), (2, 1), (4, 4)])
        p1 = ellipse.flattening(distance=0.01)
        p2 = bspline.flattening(distance=0.01)
        res = intersect_polylines_2d(Vec2.list(p1), Vec2.list(p2))
        assert len(res) == 2

    def test_intersecting_squares(self):
        square1 = forms.close_polygon(forms.square(2.0))
        square2 = forms.translate(square1, (1, 1))
        res = intersect_polylines_2d(Vec2.list(square1), Vec2.list(square2))
        assert len(res) == 2
        res.sort()
        assert res[0].isclose(Vec2(1, 2))
        assert res[1].isclose(Vec2(2, 1))

    def test_squares_with_common_corner_vertex(self):
        square1 = forms.close_polygon(forms.square(2.0))
        square2 = forms.translate(square1, (2, 2))
        res = intersect_polylines_2d(Vec2.list(square1), Vec2.list(square2))
        assert len(res) == 1
        assert res[0].isclose(Vec2(2, 2))

    def test_coincident_common_segment(self):
        """ The common segment does not create intersection points.
        Same as intersection of coincident lines!
        """
        pline1 = Vec2.list([(1, 1), (2, 1)])
        pline2 = Vec2.list([(1, 1), (2, 1)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 0

    def test_coincident_common_last_segment(self):
        """ The common segment does not create intersection points, but the
        preceding segment does.
        """
        pline1 = Vec2.list([(0, 0), (1, 1), (2, 1)])
        pline2 = Vec2.list([(0, 2), (1, 1), (2, 1)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 1
        assert res[0].isclose(Vec2(1, 1))

    def test_coincident_common_intermediate_segment(self):
        """ The common segment does not create intersection points, but the
        preceding and the following segment does.
        """
        pline1 = Vec2.list([(0, 0), (1, 1), (2, 1), (3, 0)])
        pline2 = Vec2.list([(0, 2), (1, 1), (2, 1), (3, 2)])
        res = intersect_polylines_2d(pline1, pline2)
        assert len(res) == 2
        res.sort()
        assert res[0].isclose(Vec2(1, 1))
        assert res[1].isclose(Vec2(2, 1))

    def test_endpoint_close_to_line(self):
        """ The one line's endpoint is close to the other line but in a way
        that the bbox's do not overlap
        """
        pline1 = Vec2.list([(0, 0), (0, 1)])
        pline2 = Vec2.list([(1e-12, 0.5), (1, 0.5)])
        res = intersect_polylines_2d(pline1, pline2, abs_tol=1e-6)
        assert len(res) > 0

    def test_endpoints_close_together(self):
        """ Endpoints almost touching but not quite.
        """
        pline1 = Vec2.list([
            (2258.792544958331, 895.3182883002858),
            (2259.2883041920322, 895.6019850600767),
            (2259.7794999008347, 895.8935118083691)
        ])

        pline2 = Vec2.list([
            (2259.779499900837, 895.8935118083705),
            (2241.1607099887274, 926.7048840953805)
        ])
        res = intersect_polylines_2d(pline1, pline2, abs_tol=1e-10)
        assert len(res) > 0

        res = intersect_polylines_2d(pline1, pline2, abs_tol=1e-16)
        assert len(res) == 0

        res = intersect_polylines_2d(pline1[1:], pline2, abs_tol=1e-10)
        assert len(res) > 0

class TestIntersectPolylines3d:
    """
    The 3D line intersection function is tested in test suite 614.

    The basic polyline intersection algorithm is tested in class TestIntersectPolylines2d.

    This class tests only if the function intersect_polylines_3d() is implemented.

    """
    def test_intersecting_single_segments(self):
        pline1 = Vec3.list([(0, 1), (2, 1)])
        pline2 = Vec3.list([(1, 0), (1, 2)])
        res = intersect_polylines_3d(pline1, pline2)
        assert len(res) == 1
        assert res[0].isclose(Vec3(1, 1))

    def test_intersecting_single_vertical_segment(self):
        pline1 = Vec3.list([(0, 0, 0), (2, 0, 0)])
        pline2 = Vec3.list([(1, 0, 0), (1, 0, 1)])
        res = intersect_polylines_3d(pline1, pline2)
        assert len(res) == 1
        assert res[0].isclose(Vec3(1, 0))

    def test_none_intersecting_single_segments(self):
        pline1 = Vec3.list([(0, 0), (2, 0)])
        pline2 = Vec3.list([(0, 1), (2, 1)])
        res = intersect_polylines_3d(pline1, pline2)
        assert len(res) == 0


if __name__ == "__main__":
    pytest.main([__file__])
