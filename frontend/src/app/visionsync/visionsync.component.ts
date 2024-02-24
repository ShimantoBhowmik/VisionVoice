import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-visionsync',
  templateUrl: './visionsync.component.html',
  styleUrls: ['./visionsync.component.scss'],
})
export class VisionsyncComponent {
  file: File | null = null;
  textualDescription: boolean = false;
  audioDescription: boolean = false;
  summarization: boolean = false;

  syncs: any = [];
  recap: any = [];

  onFileSelected(event: any) {
    this.file = event.target.files[0];
  }

  toggleTextualDescription(event: Event) {
    this.textualDescription = !this.textualDescription;
  }
  toggleAudioDescription(event: Event) {
    this.audioDescription = !this.audioDescription;
  }
  toggleSummarization(event: Event) {
    this.summarization = !this.summarization;
  }

  generateVideoDescription() {
    this.syncs = [];
    this.recap = '';
    if (this.file === null) {
      return;
    }

    const formData = new FormData();
    const blob = new Blob([this.file], { type: this.file.type });
    formData.append('video', blob);
    const url =
      'http://localhost:8000/visionsync?text=' +
      this.textualDescription +
      '&audio=' +
      this.audioDescription +
      '&desc=' +
      this.summarization;

    fetch(url, {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.text())
      .then((data) => {
        const split = data.split('\n').filter((x) => x !== '');
        if (this.summarization) {
          this.recap = JSON.parse(split.pop()!).description.split('\n');
        }

        this.syncs = split.map((sync: string) => {
          return JSON.parse(sync);
        });
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }
}
