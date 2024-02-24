import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { VisionsyncComponent } from './visionsync/visionsync.component';
import { StreamsyncComponent } from './streamsync/streamsync.component';
import { HomeComponent } from './home/home.component';
import { SyncComponent } from './sync/sync.component';

@NgModule({
  declarations: [
    AppComponent,
    VisionsyncComponent,
    StreamsyncComponent,
    HomeComponent,
    SyncComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
