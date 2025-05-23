import { Injectable, inject } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { catchError, tap, retryWhen, delay, Observable, Subject, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket$: WebSocketSubject<any> = this.getNewWebSocket();
  private connectionStatus$ = new Subject<boolean>();
  private readonly RECONNECT_INTERVAL = 5000;
  private readonly WS_ENDPOINT = 'ws://localhost:8000/ws';

  constructor() {
    this.connect();
  }

  private getNewWebSocket(): WebSocketSubject<any> {
    return webSocket({
      url: this.WS_ENDPOINT,
      closeObserver: {
        next: () => {
          console.log('WebSocket connection closed');
          this.connectionStatus$.next(false);
          this.scheduleReconnect();
        }
      },
      openObserver: {
        next: () => {
          console.log('WebSocket connection opened');
          this.connectionStatus$.next(true);
        }
      }
    });
  }

  private connect(): void {
    this.socket$ = this.getNewWebSocket();

    this.socket$.pipe(
      catchError(error => {
        console.error('WebSocket error:', error);
        this.connectionStatus$.next(false);
        return throwError(() => error);
      })
    ).subscribe();
  }

  private scheduleReconnect(): void {
    setTimeout(() => {
      console.log('Attempting to reconnect...');
      this.socket$ = this.getNewWebSocket();
      this.connect();
    }, this.RECONNECT_INTERVAL);
  }

  public getMessages(): Observable<any> {
    return this.socket$.asObservable();
  }

  public getConnectionStatus(): Observable<boolean> {
    return this.connectionStatus$.asObservable();
  }

  public sendMessage(msg: any): void {
    this.socket$?.next(msg);
  }

  public closeConnection(): void {
    this.socket$?.complete();
  }
}