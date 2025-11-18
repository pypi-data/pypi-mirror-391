# Transaction Patterns

This directory contains YAML files with transaction patterns for generating card transactions.

## Structure

- `general.yml`: Contains transaction patterns that are common to all countries.
- `eea.yml`: Contains transaction patterns specific to EEA (European Economic Area) countries.
- `[country_code].yml`: Contains transaction patterns specific to a country. For example, `portugal.yml` contains patterns for Portugal.

## Pattern Format

Each pattern is a YAML object with the following fields:

### Required Fields

- `title`: The merchant name. Can be a string or a template object for dynamic generation.
- `currency`: The currency of the transaction (3-letter currency code).
- `amount_range`: A dictionary with `min` and `max` values for the transaction amount.
- `amount_format`: An integer that controls the rounding of the generated transaction amount.
  - A positive integer `n` rounds the amount to `n` decimal places (e.g., `2` for `12.34`).
  - `0` rounds the amount to the nearest whole number (e.g., `12`).
  - A negative integer `-n` rounds the amount to the nearest `10^|n|` (e.g., `-2` for rounding to the nearest 100, like `100`, `200`).
- `types`: An array of tags categorizing the merchant (e.g., `["shopping", "groceries"]`).

### Optional Fields

- `weight` (optional): The relative probability weight for pattern selection. Defaults to 1000.
- `refund_probability` (optional): The probability (from 0.0 to 1.0) that a transaction will be refunded. If not provided, defaults to system default.
- `refundDelayMinHours` (optional): The minimum number of hours after a transaction that a refund can be generated. Defaults to 72.
- `refundDelayMaxHours` (optional): The maximum number of hours after a transaction that a refund can be generated. Defaults to 288.
- `numberOfOccurrences` (optional): The maximum number of times this transaction pattern can be used globally across a statement. If not provided, allows unlimited use.
- `subscription_frequency_days` (optional): The frequency in days for recurring transactions. If provided, additional transactions will be generated every `subscription_frequency_days` days from the initial occurrence.

### Template Titles

The `title` field supports dynamic generation using templates:

```yaml
title:
  type: template
  template: "Revolut**{num}* DUBLIN"
  params:
    num:
      generator: random_digits
      length: 4
      global_constant: true
```

#### Supported Generators

- `random_digits`: Generates random digit strings
  - `length`: Number of digits
  - `zero_pad`: Whether to pad with leading zeros (default: true)
- `random_alnum`: Generates random alphanumeric strings
  - `length`: Number of characters
  - `charset`: Custom character set (optional)
- `choice`: Selects from a list of options
  - `options`: Array of possible values
  - `weights`: Optional array of selection weights

#### Supported Transforms

- `transform.case`: Apply case transformation
  - `upper`: Convert to uppercase
  - `lower`: Convert to lowercase
  - `title`: Convert to title case

#### Global Constants

- `global_constant: true`: Ensures the same value is used across all instances of this parameter within a statement generation session.

## Schema

The JSON schema for the transaction patterns is available at [`schema.json`](schema.json).

## Creating Transaction Patterns

To create new transaction patterns, refer to the [Transaction Pattern Creation Guide](transaction_pattern_creation.md).
