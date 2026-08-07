import { Component, SimpleChanges, inject, ChangeDetectionStrategy, input } from '@angular/core';

import { OrderEventResponse } from '../order/order-event-response';
import { MatCardModule } from '@angular/material/card';
import { AILoggerService } from 'src/app/logger/ai-logger.service';

@Component({
    changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'app-checkout-response',
  standalone: true,
  imports: [MatCardModule],
  templateUrl: './checkout-response.component.html',
  styleUrls: ['./checkout-response.component.scss']
})
export class CheckoutResponseComponent {
  readonly response = input<OrderEventResponse | null>(null);
  logger = inject(AILoggerService);

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['response']) {
      this.logger.logEvent('checkout response', changes['response'].currentValue);
    }
  }
}
