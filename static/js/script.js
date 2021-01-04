$(document).ready(function(){

    // Animates Business Cards
    $(".bus-results").delay(300).animate({
        opacity: '1',
    }, 300);

    // Delete Profile and Buisness function 
    $(".delete").click(function(){
        $(".del-dsply").show()
    })

    $(".cancel").click(function(){
        $(".del-dsply").hide()
    })

  });