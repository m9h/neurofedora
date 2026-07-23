// Minimal vtk-mpich/vtk-openmpi smoke test: spin up a vtkMPIController and
// verify a parallel reduce produces the analytically-known sum. This exercises
// the MPI-parallel VTK build (vtkMPIController lives in the ParallelMPI module,
// which the serial vtk package does NOT ship) and the MPI runtime it links.
//
// Each rank contributes (rank+1); a SUM reduce to root must equal the
// triangular number nproc*(nproc+1)/2. Exit non-zero on mismatch so ctest
// flags a regression.

#include <vtkMPIController.h>
#include <vtkCommunicator.h>
#include <vtkSmartPointer.h>

#include <iostream>

int main(int argc, char* argv[])
{
  vtkSmartPointer<vtkMPIController> controller =
    vtkSmartPointer<vtkMPIController>::New();
  controller->Initialize(&argc, &argv, /*initializedExternally=*/0);

  const int rank = controller->GetLocalProcessId();
  const int nproc = controller->GetNumberOfProcesses();

  int local = rank + 1;
  int total = 0;
  controller->Reduce(&local, &total, 1, vtkCommunicator::SUM_OP, 0);

  int rc = 0;
  if (rank == 0)
  {
    const int expected = nproc * (nproc + 1) / 2;
    std::cout << "nproc=" << nproc << " sum=" << total
              << " expected=" << expected << std::endl;
    if (total != expected)
    {
      std::cerr << "FAIL: reduce mismatch" << std::endl;
      rc = 1;
    }
  }

  controller->Finalize();
  return rc;
}
