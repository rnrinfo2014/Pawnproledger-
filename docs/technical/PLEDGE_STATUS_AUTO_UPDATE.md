# Pledge Status Auto-Update Documentation

## Overview
The pledge payment system automatically updates pledge status based on payment amounts and remaining balances. This ensures that pledge statuses accurately reflect their current payment state.

## Status Mapping

### Internal Database Statuses → API Response Statuses
- `'active'` → `'ACTIVE'` - No payments made yet
- `'partial_paid'` → `'ACTIVE'` - Some payments made, balance remaining
- `'redeemed'` → `'CLOSED'` - Fully paid, no balance remaining
- `'auctioned'` → `'DEFAULTED'` - Auction/default status

## Automatic Status Updates

### When Creating a Payment
The system automatically updates pledge status when a new payment is created:

```python
# Payment Creation Logic:
if new_balance <= 0:
    # Pledge is fully paid - mark as redeemed (CLOSED)
    pledge.status = 'redeemed'
    # Auto-add remark if not specified
    if not payment.remarks:
        payment.remarks = "Full pledge settlement - Pledge closed"
        
elif new_balance < pledge.final_amount:
    # Partial payment made - mark as partial_paid (ACTIVE)
    pledge.status = 'partial_paid'
    
# If new_balance == pledge.final_amount, status remains 'active'
```

### When Updating a Payment
When a payment amount is modified, the system recalculates total payments and updates status:

```python
# Payment Update Logic:
total_payments = sum(all_payments_for_pledge)

if total_payments >= pledge.final_amount:
    pledge.status = 'redeemed'  # CLOSED
elif total_payments > 0:
    pledge.status = 'partial_paid'  # ACTIVE
else:
    pledge.status = 'active'  # ACTIVE
```

### When Deleting a Payment
When a payment is deleted, the system recalculates remaining payments and updates status accordingly.

## Payment Examples

### Example 1: Partial Payment
```json
{
  "pledge_id": 1,
  "payment_type": "interest",
  "amount": 5000.00,
  "remarks": "Monthly interest payment"
}
```
**Result**: If pledge has remaining balance, status becomes `'partial_paid'` → API shows `'ACTIVE'`

### Example 2: Full Payment (Closing Pledge)
```json
{
  "pledge_id": 1,
  "payment_type": "full_redeem",
  "amount": 95000.00,
  "interest_amount": 5000.00,
  "principal_amount": 90000.00,
  "remarks": "Full pledge redemption"
}
```
**Result**: Balance becomes 0, status changes to `'redeemed'` → API shows `'CLOSED'`

### Example 3: Auto-Generated Remarks for Full Payment
```json
{
  "pledge_id": 1,
  "payment_type": "full_redeem",
  "amount": 95000.00
  // No remarks provided
}
```
**Result**: 
- Status: `'redeemed'` → `'CLOSED'`
- Auto-generated remarks: `"Full pledge settlement - Pledge closed"`

## API Response Examples

### Payment Response When Pledge is Closed
```json
{
  "payment_id": 101,
  "pledge_id": 1,
  "amount": 95000.00,
  "balance_amount": 0.00,
  "receipt_no": "RCPT-1-000001",
  "remarks": "Full pledge settlement - Pledge closed",
  "created_at": "2025-09-17T10:30:00"
}
```

### Pledge Listing Response (Closed Pledge)
```json
{
  "id": 1,
  "pledge_no": "PLG-001",
  "status": "CLOSED",
  "closed_at": "2025-09-17T10:30:00",
  "remaining_principal": 0.00,
  "total_payments": 95000.00
}
```

## Status Transition Flow

```
NEW PLEDGE
    ↓
[ACTIVE] ←→ [ACTIVE (partial_paid)]
    ↓              ↓
    └──→ [CLOSED (redeemed)] ←┘
             ↓
    [DEFAULTED (auctioned)]
```

### Transition Rules:
1. **Active → Partial Paid**: Any payment made (balance > 0)
2. **Partial Paid → Closed**: Payment makes balance ≤ 0
3. **Active → Closed**: Single payment that fully closes pledge
4. **Closed → Partial Paid**: Payment deleted/modified, balance > 0
5. **Partial Paid → Active**: All payments deleted

## Database Changes

### Automatic Updates
- Status changes are committed immediately with payment transactions
- No manual intervention required
- Status updates are atomic (success/rollback together)

### Closed Date Tracking
When a pledge is marked as `'redeemed'`, the system:
- Sets the status to `'redeemed'`
- The `closed_at` timestamp is calculated from the latest payment date
- This appears in API responses for reporting and audit purposes

## Business Rules

### Full Payment Detection
A pledge is considered fully paid when:
- `total_payments >= pledge.final_amount`
- OR `remaining_balance <= 0`

### Status Hierarchy
1. **Closed** (redeemed) - Highest priority, pledge cannot accept new payments
2. **Partial Paid** - Has payments but balance remaining
3. **Active** - No payments made yet

## Error Handling

### Invalid Payments
- Payments exceeding remaining balance are rejected
- Payments to closed pledges are rejected
- Status rollback occurs if payment creation fails

### Data Integrity
- Status updates are part of the payment transaction
- Database constraints prevent inconsistent states
- Automatic recalculation ensures accuracy

## Testing Scenarios

### Test 1: Single Full Payment
1. Create pledge with amount 100,000
2. Make payment of 100,000
3. Verify status changes to CLOSED
4. Verify balance is 0

### Test 2: Multiple Payments to Closure
1. Create pledge with amount 100,000
2. Make payment of 50,000 (status: ACTIVE)
3. Make payment of 50,000 (status: CLOSED)
4. Verify final status is CLOSED

### Test 3: Payment Modification
1. Create pledge, make partial payment
2. Update payment to full amount
3. Verify status changes to CLOSED
4. Reduce payment amount
5. Verify status reverts to ACTIVE

This automatic status management ensures data consistency and provides clear pledge lifecycle tracking without manual intervention.