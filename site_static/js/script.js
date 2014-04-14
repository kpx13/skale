$(document).ready(function(){

  $('.side-nav ul ul').hide();
  $('.side-nav .active ul').show();

  $('.side-nav > ul > li > span').click(function(){
    var tab = $(this).next('ul');
    if(tab.is(':visible')){
      $(this).parent('li').removeClass('active');
      tab.slideUp();
    } else {
      tab.slideDown();
      $(this).parent('li').addClass('active');
    }
  });



  jQuery('input[placeholder], textarea[placeholder]').placeholder();

});


