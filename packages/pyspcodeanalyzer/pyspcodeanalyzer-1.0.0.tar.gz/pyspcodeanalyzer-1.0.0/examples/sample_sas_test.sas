/* %include Sample SAS program */
libname mylib '/data/';
%include 'macros.sas';
%include 'data_calc.sas';

data work.sales;
  set mylib.transactions;
  if amount > 1000 then category = 'High';
  else category = 'Low';
run;

proc sql;
  create table summary as
  select region, sum(amount) as total
  from work.sales
  group by region;
quit;

%macro report();
  proc print data=summary; run;
%mend;
%report;

ods html file='report.html' style=statistical;
proc means data=summary;
run;
ods html close;
