import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from "../app/home/home.component";
import { StreamsyncComponent } from './streamsync/streamsync.component';
import { VisionsyncComponent } from './visionsync/visionsync.component';

const routes: Routes = [
    { path: 'home', component: HomeComponent },
    { path: 'streamsync', component: StreamsyncComponent },
    { path: 'visionsync', component: VisionsyncComponent },
    { path: '', redirectTo: '/home', pathMatch: 'full' }

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }