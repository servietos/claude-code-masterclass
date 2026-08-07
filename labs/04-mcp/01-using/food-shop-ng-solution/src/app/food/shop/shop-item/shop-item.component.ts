import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { CatalogItem } from '../../catalog-item.model';
import { CartItem } from '../cart-item.model';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { EuroPipe } from '../../../shared/euro.pipe';
import { NumberPickerComponent } from '../../../shared/number-picker/number-picker.component';
import { MatCardModule } from '@angular/material/card';

@Component({
    changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'app-shop-item',
  templateUrl: './shop-item.component.html',
  styleUrls: ['./shop-item.component.scss'],
  standalone: true,
  imports: [
    MatCardModule,
    NumberPickerComponent,
    ReactiveFormsModule,
    EuroPipe,
  ],
})
export class ShopItemComponent {
  readonly food = input<CatalogItem>(new CatalogItem());
  readonly inCart = input<number | null>(0);
  readonly amountChange = output<CartItem>();
  nbrPicker = new FormControl(this.inCart());

  ngOnChanges() {
    this.nbrPicker.setValue(this.inCart());
  }

  handleAmountChange(amount: number) {
    let ci: CartItem = {
      id: this.food().id,
      name: this.food().name,
      price: this.food().price,
      quantity: amount,
    };
    this.amountChange.emit(ci);
  }
}
