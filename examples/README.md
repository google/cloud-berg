
### Example image creation script for `cloud-berg`
```bash
export source_image_project=your-project-name
export golden_image_src_instance='devbox-4p100--hvuk5l'
export image_name='berg-0-0-20-cuda-9-tf-1-8-0-torch-0-4-0'
export description="Ubuntu\ 16.04\ w/\ CUDA\ 9.0\ CUDNN\ 7\ tf=1.8,\ pytorch=0.4.0"

gcloud compute instances stop $golden_image_src_instance && \
gcloud compute \
  --project=google.com:tom-experiments images create $image_name \
  --description=$description \
  --source-disk=$golden_image_src_instance \
  --source-disk-zone=us-west1-b && \
gcloud compute \
  --project=cloud-berg images create $image_name \
  --description=$description \
  --source-image=$image_name \
  --source-image-project=$source_image_project
```