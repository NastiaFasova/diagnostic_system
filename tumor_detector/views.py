from pathlib import Path
from django.shortcuts import render
import nibabel as nib
import torch
import cv2
import matplotlib.pyplot as plt
import numpy as np
from celluloid import Camera
import os
import shutil

from tumor_detector.TumorSegmentation import TumorSegmentation


def image_upload(request):
    return render(request, 'image_upload.html')


def upload(request):
    if request.method == 'POST':
        gz_file = request.FILES['gz_file']
        if gz_file.name.endswith('.gz'):

            destination_directory = 'temp_files_directory/'
            destination_path = os.path.join(destination_directory, gz_file.name)

            with open(destination_path, 'wb') as destination_file:
                shutil.copyfileobj(gz_file, destination_file)

            filename = destination_directory + gz_file.name

            data = nib.load(filename)
            ct = data.get_fdata()
            fig = plt.figure()
            camera = Camera(fig)

            for i in range(0, ct.shape[2], 2):  # axial view
                plt.imshow(ct[:, :, i], cmap="bone")
                camera.snap()  # Store the current slice
            animation = camera.animate()  # create the animation
            # animation.save('the_movie.mp4', writer='ffmpeg', fps=15)
            video_url = os.path.join('media', 'visualise.mp4')
            animation.save(video_url, writer='ffmpeg', fps=15)
            # Render the upload form
            return render(request, 'image_upload.html', {'video_url': video_url})


def analyze(request):
    if request.method == 'POST':
        gz_file = request.FILES['gz_file_analyze']
        if gz_file.name.endswith('.gz'):

            destination_directory = 'temp_files_directory/'
            destination_path = os.path.join(destination_directory, gz_file.name)

            with open(destination_path, 'wb') as destination_file:
                shutil.copyfileobj(gz_file, destination_file)

            filename = destination_directory + gz_file.name

            path = 'ai_model/model.ckpt'

            model = TumorSegmentation.load_from_checkpoint(path)
            optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
            checkpoint = torch.load(path, map_location=torch.device('cpu'))
            model.load_state_dict(checkpoint['state_dict'])
            optimizer.load_state_dict(checkpoint['optimizer_states'][0])

            model.eval()

            THRESHOLD = 0.5
            subject = Path(filename)
            ct = nib.load(subject).get_fdata() / 3071  # standardize
            ct = ct[:, :, 30:]  # crop

            segmentation = []
            label = []
            scan = []

            for i in range(ct.shape[-1]):
                slice = ct[:, :, i]
                slice = cv2.resize(slice, (256, 256))
                slice = torch.tensor(slice)
                scan.append(slice)
                slice = slice.unsqueeze(0).unsqueeze(0).float()

                with torch.no_grad():
                    pred = model(slice)[0][0].cpu()
                pred = pred > THRESHOLD
                segmentation.append(pred)
                label.append(segmentation)
            # save segmentation and label variables into file(to see what inside)

            # Plotting the predicted segmentation (red)
            fig = plt.figure()
            camera = Camera(fig)  # create the camera object from celluloid

            for i in range(0, len(scan), 2):  # Sagital view. Skip every second slice to reduce the video length
                plt.imshow(scan[i], cmap="bone")
                mask = np.ma.masked_where(segmentation[i] == 0, segmentation[i])
                plt.imshow(mask, alpha=0.5, cmap="autumn")  # Use autumn colormap to get red segmentation

                plt.axis("off")
                camera.snap()  # Store the current slice
            animation = camera.animate()  # create the animation

            # animation.save('the_movie.mp4', writer='ffmpeg', fps=15)
            analyze_video_url = os.path.join('media', 'analyze.mp4')
            animation.save(analyze_video_url, writer='ffmpeg', fps=15)
            # Render the upload form
            return render(request, 'image_upload.html', {'analyze_video_url': analyze_video_url})
