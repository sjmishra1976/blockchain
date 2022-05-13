//sanmiscoin ico
//version of compiler
pragma solidity >=0.4.14 <0.9.0;

contract sanmiscoin_ico{
    //introducing the max number of sanmiscoin avilable for sale
    uint public max_sanmiscoins = 1000000;

    //Introducing USD to sanmiscoin conversion rate
    uint public usd_to_sanmiscoins = 1000;

    //Intrducing total number of sanmiscoins that have been bought by investors
    uint public total_sanmiscoins_bought = 0;

    //Mapping from the investor address to its equity in sanmiscoin and USD
    mapping(address => uint) equity_sanmicoins;
    mapping(address => uint) equity_usd;

    //checking if investor can buy sanmiscoin
    modifier can_buy_sanmiscoins(uint usd_invested) {
        require(usd_invested * usd_to_sanmiscoins + total_sanmiscoins_bought <  max_sanmiscoins );
        _;

    }
    
   //gettimg the equity in sanmiscoin of an investor
     function equity_in_sanmiscoins(address investor) external constant returns (uint){
       return equity_sanmicoins[investor];

   }

    //gettimg the equity in USD of an investor
      function equity_in_usd(address investor) external constant returns (uint){
       return equity_usd[investor];

   }

   //Buying sanmiscoins
    function buy_sanmiscoins(address investor, uint usd_invested) external 
    can_buy_sanmiscoins(usd_invested){
        uint sanmiscoins_bought = usd_invested * usd_to_sanmiscoins;
        equity_sanmicoins[investor] += sanmiscoins_bought;
        equity_usd[investor] = equity_sanmicoins[investor]/usd_to_sanmiscoins;
        total_sanmiscoins_bought += sanmiscoins_bought;

    }

    //Selling sanmiscoins
    function sell_sanmiscoins(address investor, uint sanmiscoins_sold) external {
        equity_sanmicoins[investor] -= sanmiscoins_sold;
        equity_usd[investor] = equity_sanmicoins[investor]/usd_to_sanmiscoins;
        total_sanmiscoins_bought -= sanmiscoins_sold;

    }
}