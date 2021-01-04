$(document).ready(function(){

    // Animates Business Cards
    $(".bus-results").delay(300).animate({
        opacity: '1',
    }, 800);

    // Animates forms
    $(".login-cont").delay(300).animate({
        opacity: '1',
    }, 500);

    // Animates search box
    $(".search-tool").animate({
        opacity: '1',
    }, 500);

    // Delete Profile and Buisness function 
    $(".delete").click(function(){
        $(".del-dsply").show()
    })

    // Cancel Delete function
    $(".cancel").click(function(){
        $(".del-dsply").hide()
    })

    // Flash Messsage Animation
    $(".flashes").fadeOut(8000);

  });