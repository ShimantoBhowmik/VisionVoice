import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-sync',
  templateUrl: './sync.component.html',
  styleUrls: ['./sync.component.scss'],
})
export class SyncComponent {
  @Input() timestamp: string = '';
  @Input() description: string = '';
  @Input() audio: string = '';
}
