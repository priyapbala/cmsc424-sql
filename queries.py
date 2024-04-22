queries = ["" for i in range(0, 19)]

### 0. Report the votes for the normal (i.e, not special) Senate Election in Maryland in 2018.
### Output column order: candidatename, partyname, candidatevotes
### Order by candidatename ascending
queries[0] = """
select candidatename, partyname, candidatevotes
from sen_state_returns
where specialelections = False and year = 2018 and statecode = 'MD'
order by candidatename;
"""

### 1. Write a query to find the maximum, minimum, and average population in 2010 across all states.
### The result will be a single row.
### Truncate the avg population to a whole number using trunc
### Output Columns: max_population, min_population, avg_population
queries[1] = """
select max(population_2010) as max_population, min(population_2010) as min_population, trunc(avg(population_2010)) as avg_population
from states;
"""

### 2. Write a query to find the candidate with the maximum votes in the 2008 MI Senate Election. 
### Output Column: candidatename
### Order by: candidatename
queries[2] = """
select candidatename
from sen_state_returns
where candidatevotes = (select max(candidatevotes) from sen_state_returns where year = 2008 and statecode = 'MI')
order by candidatename;
"""

### 3. Write a query to find the number of candidates who are listed in the sen_state_returns table for each senate election held in 2018. 
### Note that there may be two elections in some states, and there should be two tuples in the output for that state.
### 'NA' or '' (empty) should be treated as candidates. 
### Output columns: statecode, specialelections, numcandidates
### Order by: statecode, specialelections
queries[3] = """
select statecode, specialelections, count(candidatename) as numcandidates
from sen_state_returns
where year = 2018
group by statecode, specialelections
order by statecode, specialelections;
"""

### 4. Write a query to find, for the 2008 elections, the number of counties where Barack Obama received strictly more votes 
### than John McCain.
### This will require you to do a self-join, i.e., join pres_county_returns with itself.
### Output columns: num_counties
queries[4] = """
select count(p1.countyname) as num_counties
from pres_county_returns p1 join pres_county_returns p2 on 
(p1.year = p2.year and p1.statecode = p2.statecode and p1.countyname = p2.countyname)
where p1.candidatename = 'Barack Obama' and p2.candidatename = 'John McCain' and p1.candidatevotes > p2.candidatevotes and p1.year = 2008;
"""

### 5. Write a query to find the names of the states with at least 100 counties in the 'counties' table.
### Use HAVING clause for this purpose.
### Output columns: statename, num_counties
### Order by: statename
queries[5] = """
select states.name as statename, count(states.name) as num_counties
from states join counties on (states.statecode = counties.statecode)
group by states.name
having(count(counties.name) >= 100)
order by statename;
"""

### 6. Write a query to construct a table:
###     (statecode, total_votes_2008, total_votes_2012)
### to count the total number of votes by state for Barack Obama in the two elections.
###
### Use the ability to "sum" an expression (e.g., the following query returns the number of counties in 'AR')
### select sum(case when statecode = 'AR' then 1 else 0 end) from counties;
###
### Order by: statecode
queries[6] = """
select statecode, sum(case when (candidatename = 'Barack Obama' and year = 2008) then candidatevotes else 0 end) as total_votes_2008, sum(case when (candidatename = 'Barack Obama' and year = 2012) then candidatevotes else 0 end) as total_votes_2012
from pres_county_returns
group by statecode
order by statecode;
"""

### 7. Create a table to list the disparity between the populations listed in 'states' table and those listed in 'counties' table for 1950 and 2010.
### Result should be: 
###        (statename, disparity_1950, disparity_2010)
### So disparity_1950 = state population 1950 - sum of population_1950 for the counties in that state
### Use HAVING to only output those states where there is some disparity (i.e., where at least one of the two is non-zero)
### Order by statename
queries[7] = """
select states.name as statename, (states.population_1950 - sum(case when counties.statecode = states.statecode then counties.population_1950 else 0 end)) as disparity_1950,
(states.population_2010 - sum(case when counties.statecode = states.statecode then counties.population_2010 else 0 end)) as disparity_2010
from states join counties on (states.statecode = counties.statecode)
group by statename, states.population_1950, states.population_2010
having (states.population_1950 - sum(case when counties.statecode = states.statecode then counties.population_1950 else 0 end)) != 0 or 
(states.population_2010 - sum(case when counties.statecode = states.statecode then counties.population_2010 else 0 end)) != 0
order by statename;
"""

### 8. Use 'EXISTS' or 'NOT EXISTS' to find the states where no counties have population in 2010 above 500000 (500 thousand).
### Output columns: statename
### Order by statename
queries[8] = """
select states.name as statename
from states
where not exists(select * from counties where states.statecode = counties.statecode and population_2010 > 500000)
order by statename;
"""

### 9. List all counties and their basic information that have a unique name across all states. 
### Use scalar subqueries to simplify the query.
### Output columns: all attributes of counties (name, statecode, population_1950, population_2010)
### Order by name, statecode
queries[9] = """
with tempcount as (select name as countyname, count(name) as count
        from counties
        group by countyname
        order by count)
select name, statecode, population_1950, population_2010
from tempcount join counties on (tempcount.countyname = counties.name)
where count = 1
order by name, statecode;
"""

### 10. Identify counties that witnessed a population decline between 1950 - 2010 despite belonging to states that witnessed a population growth in the same period. 
### Ouput columns: name, statecode, population_decline
### Order by: population_decline descending.
### Possible solution:
queries[10] = """
select counties.name, counties.statecode, abs((counties.population_2010 - counties.population_1950)) as population_decline
from states join counties on (states.statecode = counties.statecode)
where (counties.population_2010 - counties.population_1950) < 0 and (states.population_2010 - states.population_1950) > 0
order by population_decline;
"""

### 11. Use Set Intersection to find the counties that Barack Obama lost in 2008, but won in 2012.
###
### Output columns: countyname, statecode
### Order by countyname, statecode
queries[11] = """
with temp2008 as (select countyname, statecode, max(candidatevotes) as maxvotes2008
        from pres_county_returns
        where year = 2008
        group by countyname, statecode),
temp2012 as (select countyname, statecode, max(candidatevotes) as maxvotes2012
        from pres_county_returns
        where year = 2012
        group by countyname, statecode)
(select temp2008.countyname, temp2008.statecode
from pres_county_returns join temp2008 on (pres_county_returns.countyname = temp2008.countyname and pres_county_returns.statecode = temp2008.statecode)
where candidatename = 'Barack Obama' and candidatevotes < maxvotes2008 and year = 2008)
intersect
(select temp2012.countyname, temp2012.statecode
from pres_county_returns join temp2012 on (pres_county_returns.countyname = temp2012.countyname and pres_county_returns.statecode = temp2012.statecode)
where candidatename = 'Barack Obama' and candidatevotes = maxvotes2012 and year = 2012)
order by countyname, statecode;
"""

### 12. The anti-join of two relations A and B over some predicate P is defined to be the all of the tuples
### A_i of relation A where there is no matching B_j in B such that (A_i, B_j) satisfies P.
### When exploring unknown datasets the anti-join can be useful to identify anomalies or inconsistencies in  
### names and identifiers across tables in the dataset.
### Find the anti-join of `counties` with `pres_county_returns` to identify counties from the `counties` table
### where no votes have been recorded.
### Output columns: statecode, name
### Order by: statecode, name
queries[12] = """
select statecode, name
from counties
where name not in (select countyname from pres_county_returns where counties.statecode = pres_county_returns.statecode)
order by statecode, name;
"""

### 13. Find all presidential candidates listed in pres_county_returns who also ran for senator.
### HINT: Use "intersect" to simplify the query
###
### Every candidate should be reported only once. 
###
### Output columns: candidatename
### Order by: candidatename
queries[13] = """
(select candidatename from pres_county_returns)
intersect
(select candidatename from sen_state_returns)
order by candidatename
limit 3;
"""

### 14. Create a table listing the months and the number of states that were admitted to the union (admitted_to_union field) in that month.
### Use 'extract' for operating on dates, and the ability to create a small inline table in SQL. For example, try:
###         select * from (values(1, 'Jan'), (2, 'Feb')) as x;
###
### Output columns: month_no, monthname, num_states_admitted
### month should take values: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec
### Order by: month_no
queries[14] = """
select month_no, monthname, count(admitted_to_union) as num_states_admitted
from (values(1, 'Jan'), (2, 'Feb'), (3, 'Mar'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'), 
(9, 'Sep'), (10, 'Oct'), (11, 'Nov'), (12, 'Dec')) as x (month_no, monthname)
left join states on (extract(month from admitted_to_union) = month_no)
group by month_no, monthname
order by month_no;
"""

### 15. Create a view pres_state_votes with schema (year, statecode, candidatename, partyname, candidatevotes) where we maintain aggregated counts by statecode (i.e.,
### candidatevotes in this view would be the total votes for each state, including states with statecode 'NA'). XX
queries[15] = """
create view pres_state_votes as
select year, statecode, candidatename, partyname, sum (candidatevotes) as candidatevotes
from pres_county_returns
group by year, statecode, candidatename, partyname;
"""

### 16. Use a single ALTER TABLE statement to add (name, statecode) as primary key to counties, and to add CHECKs that neither of the two populations are less than zero.
### Name the two CHECK constraints nonzero2010 and nonzero1950. XX
queries[16] = """
alter table counties 
add primary key (name, statecode),
add constraint nonzero2010 check (population_2010 >= 0),
add constraint nonzero1950 check (population_1950 >= 0);
"""

### 17. Create a list of percentage each presidential candidate won in each state, in each year, and
### show only the top 10 (among all year and state) in descending order. "totalvotes" should be the total
### votes cast in the presidential election for each year and state. "percentvote" should be a float
### with one digit to the right of the decimal point.
### Output columns: year, statecode, candidatename, candidatevotes, totalvotes, percentvote
### Order by: percentvote desc, year asc, candidatename asc, limit to 10 lines
queries[17] = """
with tempvotes as (select statecode, year, sum(candidatevotes) as totalvotes
        from pres_county_returns 
        group by statecode, year)
select tempvotes.year, tempvotes.statecode, candidatename, sum(candidatevotes) as candidatevotes, totalvotes, 
round(cast(sum(candidatevotes) as numeric)/tempvotes.totalvotes*100, 1) as percentvote
from tempvotes join pres_county_returns on (tempvotes.statecode = pres_county_returns.statecode and tempvotes.year = pres_county_returns.year)
where totalvotes != 0
group by tempvotes.year, tempvotes.statecode, candidatename, totalvotes
order by percentvote desc, year asc, candidatename asc
limit 10;
"""

### 18. Create a list of percentage of people who turned out to vote for each state in the presidential election of 2000
### in descending order. "percentturnout" should be a float with one digit to the right of the decimal point.
### Output columns: statecode, percentturnout
### Order by: percentageturnout desc;
queries[18] = """
with tempvotes as (select statecode, sum(case when year = 2000 then candidatevotes else 0 end) as totalvotes
        from pres_county_returns 
        group by statecode)
select tempvotes.statecode, round(cast(totalvotes as numeric)/population_2000*100, 1) as percentturnout
from tempvotes join states on (tempvotes.statecode = states.statecode)
order by percentturnout desc;
"""