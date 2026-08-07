# Signals

Hold state in `signal()`, derive everything else with `computed()`, and reach for `linkedSignal()` only when a derived value must stay writable.

Never mirror one signal into another with an `effect()`; that is a `computed()` written the slow way.
