#include <itkVersion.h>
#include <itkImage.h>
#include <itkImageFileReader.h>
#include <itkImageFileWriter.h>
#include <itkDiscreteGaussianImageFilter.h>
#include <cstdlib>
#include <cstring>
#include <iostream>

using ImageType = itk::Image<float, 3>;

static ImageType::Pointer make_image()
{
  auto img = ImageType::New();
  ImageType::RegionType region;
  ImageType::IndexType  start = {{0, 0, 0}};
  ImageType::SizeType   size  = {{16, 16, 16}};
  region.SetSize(size);
  region.SetIndex(start);
  img->SetRegions(region);
  img->Allocate();
  img->FillBuffer(1.0f);
  return img;
}

static int run_version()
{
  std::cout << "ITK version: " << itk::Version::GetITKVersion() << std::endl;
  std::cout << "ITK source version: " << itk::Version::GetITKSourceVersion() << std::endl;
  return 0;
}

static int run_gaussian()
{
  auto img = make_image();
  using FilterType = itk::DiscreteGaussianImageFilter<ImageType, ImageType>;
  auto filter = FilterType::New();
  filter->SetInput(img);
  filter->SetVariance(1.5);
  try {
    filter->Update();
  } catch (const itk::ExceptionObject& e) {
    std::cerr << "gaussian failed: " << e << std::endl;
    return 1;
  }
  std::cout << "gaussian output size: " << filter->GetOutput()->GetLargestPossibleRegion().GetSize() << std::endl;
  return 0;
}

static int run_nifti()
{
  auto img = make_image();
  const char* path = "smoke_itk_out.nii.gz";
  auto w = itk::ImageFileWriter<ImageType>::New();
  w->SetFileName(path);
  w->SetInput(img);
  try { w->Update(); } catch (const itk::ExceptionObject& e) {
    std::cerr << "write failed: " << e << std::endl;
    return 1;
  }

  auto r = itk::ImageFileReader<ImageType>::New();
  r->SetFileName(path);
  try { r->Update(); } catch (const itk::ExceptionObject& e) {
    std::cerr << "read failed: " << e << std::endl;
    return 1;
  }
  auto out = r->GetOutput();
  auto sz = out->GetLargestPossibleRegion().GetSize();
  return (sz[0] == 16 && sz[1] == 16 && sz[2] == 16) ? 0 : 1;
}

int main(int argc, char** argv)
{
  if (argc < 2) {
    std::cerr << "usage: smoke_itk {version|gaussian|nifti}\n";
    return 2;
  }
  if (std::strcmp(argv[1], "version")  == 0) return run_version();
  if (std::strcmp(argv[1], "gaussian") == 0) return run_gaussian();
  if (std::strcmp(argv[1], "nifti")    == 0) return run_nifti();
  std::cerr << "unknown subcommand: " << argv[1] << "\n";
  return 2;
}
