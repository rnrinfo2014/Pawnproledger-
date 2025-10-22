import requests

BASE_URL = 'http://localhost:8000'
login_data = {'username': 'admin', 'password': 'admin123'}
response = requests.post(f'{BASE_URL}/token', data=login_data)
token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

test_date = '2025-10-15'
company_id = 1

print('✅ Testing Daybook Daily Summary...')
response = requests.get(f'{BASE_URL}/api/v1/daybook/daily-summary?transaction_date={test_date}&company_id={company_id}', headers=headers)
if response.status_code == 200:
    data = response.json()
    summary = data.get('summary', {})
    entries = data.get('entries', [])
    print(f'✅ SUCCESS: {len(entries)} entries found')
    print(f'   Total Debits: Rs.{summary.get("total_debit", 0):,.2f}')
    print(f'   Total Credits: Rs.{summary.get("total_credit", 0):,.2f}')
    print(f'   Balance: Rs.{summary.get("balance_difference", 0):,.2f}')
    
    if entries:
        print(f'   Sample entries:')
        for i, entry in enumerate(entries[:3]):
            voucher_type = entry.get('voucher_type', 'Unknown')
            account = entry.get('account_name', 'Unknown')
            debit = entry.get('debit', 0)
            credit = entry.get('credit', 0)
            print(f'     {i+1}. {voucher_type} - {account}: Dr.{debit} Cr.{credit}')
else:
    print(f'❌ ERROR: {response.status_code}')
    print(response.text)

print('\n✅ Testing Account-wise Summary...')
response = requests.get(f'{BASE_URL}/api/v1/daybook/account-wise-summary?transaction_date={test_date}&company_id={company_id}', headers=headers)
if response.status_code == 200:
    data = response.json()
    accounts = data.get('accounts', [])
    print(f'✅ SUCCESS: {len(accounts)} accounts with transactions')
    for i, acc in enumerate(accounts[:3]):
        name = acc.get('account_name', 'Unknown')
        code = acc.get('account_code', 'N/A')
        debit = acc.get('total_debit', 0)
        credit = acc.get('total_credit', 0)
        print(f'   {i+1}. {name} ({code}): Dr.{debit} Cr.{credit}')
else:
    print(f'❌ ERROR: {response.status_code}')
    print(response.text)