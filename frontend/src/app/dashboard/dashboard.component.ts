import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebSocketService } from '../core/services/websocket.service';
import { Subscription } from 'rxjs';
import { JsonPipe } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, JsonPipe],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  private wsService = inject(WebSocketService);
  private dataSub!: Subscription;
  
  holdingsData: any;
  connectionStatus = this.wsService.getConnectionStatus();

  ngOnInit(): void {
    this.dataSub = this.wsService.getMessages().subscribe({
      next: (data) => {
        console.log('New data received:', data);
        this.holdingsData = data;
      },
      error: (err) => console.error('WebSocket error:', err)
    });
  }

  ngOnDestroy(): void {
    this.dataSub?.unsubscribe();
    this.wsService.closeConnection();
  }
}