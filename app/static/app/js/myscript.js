$('#slider1, #slider2, #slider3').owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
        0: {
            items: 1,
            nav: false,
            autoplay: true,
        },
        600: {
            items: 3,
            nav: true,
            autoplay: true,
        },
        1000: {
            items: 5,
            nav: true,
            loop: true,
            autoplay: true,
        }
    }
})



$('.plus-cart').click(function(){
    var id = $(this).attr("pid").toString();
    var span_quantity_element = this.previousElementSibling
    
    // var eml = this.ParentNode.children[2];
    $.ajax({
        type:"GET",
        url:"/pluscart",
        data:{
            prod_id : id
        },
        success: function(data){

            span_quantity_element.innerText = data.quantity; 
            document.getElementById('amount').innerText=data.amount;
            document.getElementById('totalamount').innerText = data.totalamount;
        },
        error: function(error){
            console.log(error);
        }
    })
})

$('.minus-cart').click(function(){
    var id = $(this).attr("pid").toString();
    var span_quantity_element = this.nextElementSibling
    
    // var eml = this.ParentNode.children[2];
    $.ajax({
        type:"GET",
        url:"/minuscart",
        data:{
            prod_id : id
        },
        success: function(data){

            span_quantity_element.innerText = data.quantity; 
            document.getElementById('amount').innerText=data.amount;
            document.getElementById('totalamount').innerText = data.totalamount;
        },
        error: function(error){
            console.log(error);
        }
    })
})



$('.remove-cart').click(function(){
    var id = $(this).attr("pid").toString();
    var eml = this
    // var eml = this.ParentNode.children[2];
    $.ajax({
        type:"GET",
        url:"/removecart",
        data:{
            prod_id : id
        },
        success: function(data){
            document.getElementById('amount').innerText=data.amount;
            document.getElementById('totalamount').innerText = data.totalamount;
            eml.parentNode.parentNode.parentNode.parentNode.remove()
            document.getElementById('cartcountbadge').innerText=data.cartcount

        },
        error: function(error){
            console.log(error);
        }
    })
})



setTimeout(function () {
    document.getElementById('msg').style.display = 'none';
}, 2000);
