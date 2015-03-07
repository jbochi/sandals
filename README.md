#Sandals

Use SQL to transform [pandas](http://pandas.pydata.org/) dataframes.

Unlike [`pandasql`](https://github.com/yhat/pandasql), `sandals` does not use `sqlite`. It manipulates the dataframes directly, avoiding the overhead of moving data to and from `sqlite`.

This is a work in progress. The goal is to support all examples documented on [pandas' comparison with sql] (http://pandas.pydata.org/pandas-docs/dev/comparison_with_sql.html).

Some examples:

```
>>> import pandas as pd
>>> import sandals
>>> tips = pd.read_csv("tests/data/tips.csv")
>>> sandals.sql("SELECT total_bill, sex FROM tips LIMIT 5", locals())
   total_bill     sex
0       16.99  Female
1       10.34    Male
2       21.01    Male
3       23.68    Male
4       24.59  Female
>>> sandals.sql("SELECT * FROM tips WHERE time = 'Dinner' AND tip > 5.00 LIMIT 3", locals())
    total_bill   tip   sex smoker  day    time  size
23       39.42  7.58  Male     No  Sat  Dinner     4
44       30.40  5.60  Male     No  Sun  Dinner     4
47       32.40  6.00  Male     No  Sun  Dinner     4
>>> sandals.sql("SELECT tips.day, AVG(tip), COUNT(*) FROM tips GROUP BY tips.day;", locals())
           tip  day
day
Fri   2.734737   19
Sat   2.993103   87
Sun   3.255132   76
Thur  2.771452   62
```
