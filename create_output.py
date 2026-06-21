import pandas as pd

# Load generated feedback
df = pd.read_csv('data/feedback.csv')

# Save sample output (10 records)
output_data = df.head(10).copy()
output_data.to_csv('data/sample_output.csv', index=False)

print('✅ Output file created: data/sample_output.csv')
print(f'\nDataset Summary:')
print(f'  Total feedback records: {len(df)}')
print(f'  Sample output records: 10')

print(f'\nOutput File Columns:')
for i, col in enumerate(df.columns, 1):
    print(f'  {i}. {col}')

print(f'\nSample Analysis from Output:')
sample = df.iloc[0]
print(f'  - Service Line: {sample["service_line"]}')
print(f'  - Overall Sentiment: {sample["overall_sentiment"]}')
print(f'  - Severity Level: {sample["severity"]}')
print(f'  - Routing Department: {sample["routing_department"]}')
print(f'  - Requires Escalation: {sample["requires_escalation"]}')
