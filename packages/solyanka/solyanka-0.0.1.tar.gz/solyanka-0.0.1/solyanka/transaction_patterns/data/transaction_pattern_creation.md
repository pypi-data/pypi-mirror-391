# Transaction Pattern Creation Guide

This guide explains how to create and update transaction patterns for the synthetic bank statement generator.

## Overview

Transaction patterns are YAML files that define templates for generating realistic card payment transactions. The system supports both simple string titles and dynamic template-based titles for more realistic variation.

## File Organization

- `general.yml`: Patterns applicable to all countries
- `eea.yml`: Patterns specific to EEA (European Economic Area) countries
- `[country].yml`: Country-specific patterns (e.g., `germany.yml`, `portugal.yml`)

## Creating New Patterns

### Basic Pattern Structure

```yaml
- title: "Merchant Name"
  currency: "EUR"
  amount_range:
    min: 10.0
    max: 100.0
  amount_format: 2
  types:
    - "shopping"
    - "groceries"
  weight: 100
```

### Required Fields

1. **title**: Merchant name (string or template object)
2. **currency**: 3-letter currency code (e.g., "EUR", "USD", "GBP")
3. **amount_range**: Min/max transaction amounts
4. **amount_format**: Rounding behavior
   - Positive integers: decimal places (e.g., `2` for `12.34`)
   - `0`: whole numbers (e.g., `12`)
   - Negative integers: round to nearest 10^|n| (e.g., `-2` for nearest 100)
5. **types**: Array of merchant categories

### Optional Fields

- **weight**: Selection probability weight (default: 1000)
- **refund_probability**: Chance of generating refunds (0.0-1.0)
- **refundDelayMinHours/refundDelayMaxHours**: Refund timing constraints
- **numberOfOccurrences**: Global usage limit across statement
- **subscription_frequency_days**: Recurring transaction frequency

### Dynamic Titles with Templates

For merchants with variable identifiers, use template objects:

```yaml
- title:
    type: template
    template: "Revolut**{num}* DUBLIN"
    params:
      num:
        generator: random_digits
        length: 4
        global_constant: true
  currency: "EUR"
  amount_range:
    min: 10.0
    max: 500.0
  amount_format: -1
  types:
    - "application"
  weight: 200
```

#### Template Parameters

**Generators:**

- `random_digits`: Generate digit strings
  - `length`: Number of digits
  - `zero_pad`: Pad with leading zeros (default: true)
- `random_alnum`: Generate alphanumeric strings
  - `length`: Number of characters
  - `charset`: Custom character set (optional)
- `choice`: Select from options
  - `options`: Array of possible values
  - `weights`: Selection weights (optional)

**Modifiers:**

- `global_constant: true`: Same value across all uses in a statement
- `transform.case`: Apply case transformation ("upper", "lower", "title")

## Best Practices

1. **Realistic Amounts**: Set appropriate min/max ranges based on merchant type
2. **Proper Categories**: Use descriptive, consistent type tags
3. **Appropriate Formatting**: Match amount_format to currency and merchant type
4. **Weight Balancing**: Higher weights for more common merchants
5. **Template Usage**: Use templates for merchants with variable identifiers
6. **Global Constants**: Use for consistent identifiers (like card numbers, account IDs)

## Pattern Validation

All patterns must conform to the JSON schema in `schema.json`. The system validates:

- Required field presence
- Currency code format (3 letters)
- Amount range validity
- Template structure correctness
- Type array non-emptiness

## Examples

**Simple Grocery Store:**

```yaml
- title: "Tesco Express"
  currency: "GBP"
  amount_range:
    min: 5.0
    max: 50.0
  amount_format: 2
  types:
    - "groceries"
    - "shopping"
  weight: 120
```

**Subscription Service:**

```yaml
- title: "Netflix.com"
  currency: "EUR"
  amount_range:
    min: 13.49
    max: 13.49
  amount_format: 2
  weight: 300
  subscription_frequency_days: 30
  numberOfOccurrences: 10
  types:
    - "entertainment"
    - "subscription"
```

**Template-based Online Service:**

```yaml
- title:
    type: template
    template: "Airbnb * {code} 662-105-6167"
    params:
      code:
        generator: random_alnum
        length: 12
        charset: "abcdefghijklmnopqrstuvwxyz0123456789"
        transform:
          case: lower
  currency: "USD"
  amount_range:
    min: 70.0
    max: 900.0
  amount_format: 2
  numberOfOccurrences: 1
  refund_probability: 0.4
  types:
    - "housing"
  weight: 700
```
