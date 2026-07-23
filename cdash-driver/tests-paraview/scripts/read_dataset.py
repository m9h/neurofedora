"""Read a dataset via paraview.simple, assert point/cell counts.

Usage:
    pvbatch read_dataset.py <path> <expected_points> <expected_cells> [filter]

filter (optional, default none):
    threshold   — apply vtkThreshold on first cell-data array
    contour     — apply vtkContourFilter on first point-data array
    surface     — apply ExtractSurface (vtkDataSetSurfaceFilter)
    calculator  — apply Calculator (one*1.0)
"""
import sys

from paraview.simple import (
    Calculator, Contour, ExtractSurface, OpenDataFile, Threshold, UpdatePipeline,
)


def main(path, exp_pts, exp_cells, filt=None):
    src = OpenDataFile(path)
    if src is None:
        raise SystemExit(f"FAIL: OpenDataFile returned None for {path}")

    pipe = src
    if filt == "threshold":
        pipe = Threshold(Input=src)
    elif filt == "contour":
        pipe = Contour(Input=src)
    elif filt == "surface":
        pipe = ExtractSurface(Input=src)
    elif filt == "calculator":
        pipe = Calculator(Input=src)
        pipe.Function = "1.0"

    UpdatePipeline(proxy=pipe)
    out = pipe.GetClientSideObject().GetOutputDataObject(0)

    # Walk composite datasets (MultiBlock / PartitionedDataSetCollection).
    total_pts, total_cells = 0, 0
    if hasattr(out, "NewIterator"):
        it = out.NewIterator()
        it.InitTraversal()
        while not it.IsDoneWithTraversal():
            ds = it.GetCurrentDataObject()
            if ds is not None:
                total_pts += ds.GetNumberOfPoints()
                total_cells += ds.GetNumberOfCells()
            it.GoToNextItem()
    else:
        total_pts = out.GetNumberOfPoints()
        total_cells = out.GetNumberOfCells()

    print(f"{path}: cls={out.GetClassName()} pts={total_pts} cells={total_cells} filter={filt}")

    if total_pts != exp_pts or total_cells != exp_cells:
        raise SystemExit(
            f"FAIL: expected pts={exp_pts} cells={exp_cells}, got pts={total_pts} cells={total_cells}"
        )


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit("usage: read_dataset.py <path> <pts> <cells> [filter]")
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
         sys.argv[4] if len(sys.argv) > 4 else None)
