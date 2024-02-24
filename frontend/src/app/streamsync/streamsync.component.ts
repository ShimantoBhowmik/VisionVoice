import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';

@Component({
  selector: 'app-streamsync',
  templateUrl: './streamsync.component.html',
  styleUrls: ['./streamsync.component.scss'],
})
export class StreamsyncComponent {
  video?: HTMLVideoElement;
  button?: HTMLButtonElement;
  stream?: MediaStream;
  count: number = 0;
  descriptionId?: number;
  text = '';
  descriptionOn = false;
  syncs: any = [];
  permissionGranted = false;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.video = document.getElementById('video') as HTMLVideoElement;
    this.button = document.getElementById('button') as HTMLButtonElement;
  }

  enableVideo() {
    console.log('this.video:', this.video);
    navigator.mediaDevices
      .getUserMedia({ video: true, audio: false })
      .then((stream) => {
        this.permissionGranted = true;
        this.stream = stream;
        if (!this.video) {
          return;
        }
        console.log('stream:', stream);
        this.video.srcObject = stream;
        this.video.play();
      });
  }

  toggleDescribeVideo() {
    console.log(this.video);
    console.log(this.stream);
    if (!this.video || !this.stream) {
      console.log('No video or stream');
      return;
    }

    console.log('this.descriptionOn:', this.descriptionOn);

    if (this.descriptionOn) {
      this.descriptionOn = false;
      if (this.descriptionId != null) clearInterval(this.descriptionId);
      return;
    }

    this.descriptionOn = true;
    this.count = 0;
    const track = this.stream.getVideoTracks()[0];
    const imageCapture = new (window as any).ImageCapture(track);

    this.descriptionId = setInterval(() => {
      imageCapture.takePhoto().then((blob: any) => {
        this.uploadImageFromVideo(blob);
        this.count++;
      });
    }, 5000) as any as number;
  }

  uploadImageFromVideo(videoFile: File) {
    const formData = new FormData();
    console.log('videoFile:', videoFile);
    formData.append('image', videoFile, videoFile.name);

    // Make the HTTP request
    this.http.post('http://127.0.0.1:8000/image/live', formData).subscribe(
      (response) => {
        // Handle successful response
        const r = JSON.parse(JSON.stringify(response));
        r['time'] = `${this.count * 5}s`;
        console.log(r);
        this.syncs.push(r);
      },
      (error) => {
        // Handle error
        console.error('Error:', error);
      }
    );
  }
}
