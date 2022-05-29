/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     2022/5/27 23:15:32                           */
/*==============================================================*/


drop table if exists bank;

drop table if exists belongTo;

drop table if exists checkAccount;

drop table if exists customer;

drop table if exists customerCheck;

drop table if exists customerDeposit;

drop table if exists department;

drop table if exists depositAccount;

drop table if exists employee;

drop table if exists loan;

drop table if exists pay;

drop table if exists server;

/*==============================================================*/
/* Table: bank                                                  */
/*==============================================================*/
create table bank
(
   bankName             varchar(20) not null,
   bandCity             varchar(20) not null,
   bankAssets           decimal not null,
   primary key (bankName)
);

/*==============================================================*/
/* Table: belongTo                                              */
/*==============================================================*/
create table belongTo
(
   customerID           varchar(20) not null,
   loanID               varchar(20) not null,
   primary key (customerID, loanID)
);

/*==============================================================*/
/* Table: checkAccount                                          */
/*==============================================================*/
create table checkAccount
(
   accountID            varchar(20) not null,
   bankName             varchar(20) not null,
   accountBalance       decimal not null,
   accountRegisterDate  date not null,
   overdraft            decimal not null,
   primary key (accountID)
);

/*==============================================================*/
/* Table: customer                                              */
/*==============================================================*/
create table customer
(
   customerID           varchar(20) not null,
   customerName         varchar(20) not null,
   customerPhone        varchar(20) not null,
   customerAdress       varchar(20) not null,
   contactName          varchar(20) not null,
   contactPhone         varchar(20) not null,
   contactMail          varchar(20) not null,
   userContactRelation  varchar(20) not null,
   primary key (customerID)
);

/*==============================================================*/
/* Table: customerCheck                                         */
/*==============================================================*/
create table customerCheck
(
   customerID           varchar(20) not null,
   bankName             varchar(20) not null,
   accountID            varchar(20) not null,
   lastVisit            date not null,
   primary key (customerID, bankName)
);

/*==============================================================*/
/* Table: customerDeposit                                       */
/*==============================================================*/
create table customerDeposit
(
   customerID           varchar(20) not null,
   bankName             varchar(20) not null,
   accountID            varchar(20) not null,
   lateVisit            date not null,
   primary key (customerID, bankName)
);

/*==============================================================*/
/* Table: department                                            */
/*==============================================================*/
create table department
(
   bankName             varchar(20) not null,
   departmentID         varchar(20) not null,
   departmentName       varchar(20) not null,
   departmentType       varchar(20) not null,
   leaderID             varchar(20) not null,
   primary key (bankName, departmentID)
);

/*==============================================================*/
/* Table: depositAccount                                        */
/*==============================================================*/
create table depositAccount
(
   accountID            varchar(20) not null,
   bankName             varchar(20) not null,
   accountBalance       decimal not null,
   accountRegisterDate  date not null,
   interestRate         decimal not null,
   currencyType         varchar(20) not null,
   primary key (accountID)
);

/*==============================================================*/
/* Table: employee                                              */
/*==============================================================*/
create table employee
(
   employeeID           varchar(20) not null,
   bankName             varchar(20) not null,
   departmentID         varchar(20) not null,
   employeeName         varchar(20) not null,
   employeePhone        varchar(20) not null,
   employeeAdress       varchar(20) not null,
   employeeStartDate    date not null,
   primary key (employeeID)
);

/*==============================================================*/
/* Table: loan                                                  */
/*==============================================================*/
create table loan
(
   loanID               varchar(20) not null,
   bankName             varchar(20) not null,
   loanMoney            decimal not null,
   primary key (loanID)
);

/*==============================================================*/
/* Table: pay                                                   */
/*==============================================================*/
create table pay
(
   loanID               varchar(20) not null,
   payDate              date not null,
   payMoney             decimal not null,
   primary key (loanID)
);

/*==============================================================*/
/* Table: server                                                */
/*==============================================================*/
create table server
(
   customerID           varchar(20) not null,
   employeeID           varchar(20) not null,
   serveType            varchar(20) not null,
   primary key (customerID, employeeID)
);

alter table belongTo add constraint FK_belongTo foreign key (customerID)
      references customer (customerID) on delete restrict on update restrict;

alter table belongTo add constraint FK_belongTo2 foreign key (loanID)
      references loan (loanID) on delete restrict on update restrict;

alter table checkAccount add constraint FK_kaihu foreign key (bankName)
      references bank (bankName) on delete restrict on update restrict;

alter table customerCheck add constraint FK_cunCheck foreign key (customerID)
      references customer (customerID) on delete restrict on update restrict;

alter table customerCheck add constraint FK_gyCheck foreign key (accountID)
      references checkAccount (accountID) on delete restrict on update restrict;

alter table customerCheck add constraint FK_setCheck foreign key (bankName)
      references bank (bankName) on delete restrict on update restrict;

alter table customerDeposit add constraint FK_cusDEeposit foreign key (customerID)
      references customer (customerID) on delete restrict on update restrict;

alter table customerDeposit add constraint FK_gyDeposit foreign key (accountID)
      references depositAccount (accountID) on delete restrict on update restrict;

alter table customerDeposit add constraint FK_setDeposit foreign key (bankName)
      references bank (bankName) on delete restrict on update restrict;

alter table department add constraint FK_belong foreign key (bankName)
      references bank (bankName) on delete restrict on update restrict;

alter table depositAccount add constraint FK_kaihu2 foreign key (bankName)
      references bank (bankName) on delete restrict on update restrict;

alter table employee add constraint FK_work foreign key (bankName, departmentID)
      references department (bankName, departmentID) on delete restrict on update restrict;

alter table loan add constraint FK_ff foreign key (bankName)
      references bank (bankName) on delete restrict on update restrict;

alter table pay add constraint FK_pay foreign key (loanID)
      references loan (loanID) on delete restrict on update restrict;

alter table server add constraint FK_server foreign key (customerID)
      references customer (customerID) on delete restrict on update restrict;

alter table server add constraint FK_server2 foreign key (employeeID)
      references employee (employeeID) on delete restrict on update restrict;

