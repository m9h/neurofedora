#include <vtkVersion.h>
#include <vtkSmartPointer.h>
#include <vtkSphereSource.h>
#include <vtkPolyData.h>
#include <vtkImageData.h>
#include <vtkXMLImageDataWriter.h>
#include <cstdlib>
#include <cstring>
#include <iostream>

static int run_version()
{
  std::cout << "VTK version: " << vtkVersion::GetVTKVersion() << std::endl;
  std::cout << "VTK source version: " << vtkVersion::GetVTKSourceVersion() << std::endl;
  return 0;
}

static int run_sphere()
{
  auto sphere = vtkSmartPointer<vtkSphereSource>::New();
  sphere->SetRadius(2.5);
  sphere->SetThetaResolution(32);
  sphere->SetPhiResolution(32);
  sphere->Update();
  vtkPolyData* out = sphere->GetOutput();
  std::cout << "sphere points: " << out->GetNumberOfPoints() << std::endl;
  std::cout << "sphere cells:  " << out->GetNumberOfCells() << std::endl;
  return (out->GetNumberOfPoints() > 0 && out->GetNumberOfCells() > 0) ? 0 : 1;
}

static int run_image()
{
  auto img = vtkSmartPointer<vtkImageData>::New();
  img->SetDimensions(8, 8, 8);
  img->AllocateScalars(VTK_FLOAT, 1);

  auto w = vtkSmartPointer<vtkXMLImageDataWriter>::New();
  w->SetFileName("smoke_vtk_out.vti");
  w->SetInputData(img);
  w->SetDataModeToBinary();
  return (w->Write() == 1) ? 0 : 1;
}

int main(int argc, char** argv)
{
  if (argc < 2) {
    std::cerr << "usage: smoke_vtk {version|sphere|image}\n";
    return 2;
  }
  if (std::strcmp(argv[1], "version") == 0) return run_version();
  if (std::strcmp(argv[1], "sphere")  == 0) return run_sphere();
  if (std::strcmp(argv[1], "image")   == 0) return run_image();
  std::cerr << "unknown subcommand: " << argv[1] << "\n";
  return 2;
}
