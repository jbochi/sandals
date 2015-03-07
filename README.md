#Sandals

Use SQL to transform [pandas](http://pandas.pydata.org/) dataframes.

Unlike [`pandasql`](https://github.com/yhat/pandasql), `sandals` does not use `sqlite`. It manipulates the dataframes directly, avoiding the overhead of moving data to and from `sqlite`.

This is a work in progress. The goal is to support all examples documented on [pandas' comparison with sql] (http://pandas.pydata.org/pandas-docs/dev/comparison_with_sql.html).

Some examples:

```python
import pandas as pd
import sandals

tips = pd.read_csv("tests/data/tips.csv")
result = sandals.sql("SELECT * FROM tips WHERE time = 'Dinner' AND tip > 5.00;", locals())
print(result.shape()) #(15, 7)

print(sandals.sql("SELECT sex, count(*) FROM tips GROUP BY sex;", locals())["Female"]) #87
```
