#Import Libraries
import os
import pandas as pd
from gurobipy import Model, GRB, quicksum, max_



df_rare = pd.read_csv("https://raw.githubusercontent.com/mlssorarescout/sorareanalytics/main/mls_sorare_rare.csv")
df_rare.head()



indices = df_rare.player
points = dict(zip(indices, df_rare.Score))
cost = dict(zip(indices, df_rare.Usd))
S = 460

m = Model();

y = m.addVars(df_rare.player, vtype=GRB.BINARY, name="y")
m.setObjective(quicksum(cost[i]*y[i] for i in indices), GRB.MINIMIZE)

player_position_map = list(zip(df_rare.player, df_rare.position))
player_map = list(df_rare.player)

#add position constraints
m.addConstr(quicksum([y[i] for i, position in player_position_map if position==1])==1);

m.addConstr(quicksum([y[i] for i, position in player_position_map if position==2])>=1);
m.addConstr(quicksum([y[i] for i, position in player_position_map if position==2])<=2);

m.addConstr(quicksum([y[i] for i, position in player_position_map if position==3])>=1);
m.addConstr(quicksum([y[i] for i, position in player_position_map if position==3])<=2);

m.addConstr(quicksum([y[i] for i, position in player_position_map if position==4])>=1);
m.addConstr(quicksum([y[i] for i, position in player_position_map if position==4])<=2);

#add number of players in lineup constraint 
m.addConstr(quicksum([y[i] for i in indices])==5);

#add constraint that points + points bonus must be greater than S
m.addConstr(quicksum((points[i]+points[i]*.05)*y[i] for i in indices) >= S, name="points");

m.optimize()

results = pd.DataFrame()
                                          
for v in m.getVars():
    if v.x > 1e-6:
        results = results.append(df_rare.iloc[v.index][['player','position','Score','Usd']])
        print(v.varName, v.x)

print('Cost in USD $', m.objVal)


results.head()

