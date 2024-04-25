$(document).ready(function(){
    // Contact form handler
    var contactForm = $(".contact-form")
    var contactFormEndpoint = contactForm.attr("data-endpoint");
    var contactFormMethod = contactForm.attr("method");

    function contactSubmitSpinner(submitBtn, defaultText, readySubmit){
        if (readySubmit){
            submitBtn.addClass("disabled")
            submitBtn.html("<i class='fa-solid fa-spinner'></i> ...Sending")
        } else {
            submitBtn.removeClass("disabled")
            submitBtn.html(defaultText)
            
        }
    }
    

    contactForm.submit(function(event){
        event.preventDefault()
        var contactFormSubmitBtn = contactForm.find("[type='submit']")
        var contactFormSubmitBtnTxt = contactFormSubmitBtn.text()
        var contactFormData = contactForm.serialize()
        var thisForm = $(this)
        contactSubmitSpinner(contactFormSubmitBtn, "", true)
        $.ajax({
            method: contactFormMethod,
            url: contactFormEndpoint,
            data: contactFormData,
            success: function(){
                thisForm[0].reset()
                $.alert({
                    icon: 'fa fa-warning',
                    title: "Message Sent!",
                    content:"Thanks for your message, one of our team members will follow up with you shortly.",
                    type: 'green',
                    typeAnimated: false,
                })
                setTimeout(function(){
                    contactSubmitSpinner(contactFormSubmitBtn, contactFormSubmitBtnTxt, false)
                }, 2000)
            },
            error: function(error){
                console.log(error.responseJSON)
                var jsonData = error.responseJSON
                var errorMsg = ""
                $.each(jsonData, function(key, value){
                    errorMsg += key + ": " + value[0].message
                })
                $.alert({
                    icon: 'fa fa-warning',
                    title: "Oops!",
                    content: errorMsg,
                    type: 'orange',
                    typeAnimated: false,
                })
                setTimeout(function(){
                    contactSubmitSpinner(contactFormSubmitBtn, contactFormSubmitBtnTxt, false)
                }, 2000)
            },
        })
    })

    // Auto search on end typing
    var searchForm = $(".search-form")
    var searchInput = searchForm.find("[name='q']")
    var searchBtn = searchForm.find("[type='submit']")
    var typingTimer;
    var typingInterval = 500 // .5 seconds

    searchInput.keyup(function(event){
        // on key release
        clearTimeout(typingTimer)
        typingTimer = setTimeout(performSearch, typingInterval)
    })

    searchInput.keydown(function(event){
        // on key press
        clearTimeout(typingTimer)
    })

    function searchSpinner(){
        searchBtn.addClass("disabled")
        searchBtn.html("<i class='fa-solid fa-spinner'></i> ...Searching")
    }
    
    function performSearch(){
        searchSpinner()
        var query = searchInput.val()
        setTimeout(function(){
            window.location.href='/search/?q=' + query
        }, 1000)
    }

    // Cart table remove and +/- product
    var productForm = $(".form-product-ajax")

    productForm.submit(function(event){
        event.preventDefault();
        var thisForm = $(this);
        var actionEndpoint = thisForm.attr("data-endpoint");
        var httpMethod = thisForm.attr("method");
        var formData = thisForm.serialize();
        console.log()

        $.ajax({
            url: actionEndpoint,
            method: httpMethod,
            data: formData,
            success: function(data){
                console.log("success")
                console.log(data)
                console.log("Added", data.added)
                console.log("Removed",data.removed)
                var submitSpan = thisForm.find(".submit-span")
                if (data.added){
                    submitSpan.html('<button class="btn btn-danger" type="submit">Remove</button>')
                } else {
                    submitSpan.html('<button class="btn btn-success" type="submit">Add to Cart</button>')
                }
                var navbarCount = $(".navbar-cart-count")
                navbarCount.text(data.cartItemCount)
                var currentPath = window.location.href
                if (currentPath.indexOf("cart") != -1) {
                    refreshCart()
                }
            },
            error: function(errorData){
                $.alert({
                    icon: 'fa fa-warning',
                    title: "Oops!",
                    content:"We couldn't update your cart.  Please try again",
                    type: 'orange',
                    typeAnimated: false,
                })
                console.log("error")
                console.log(errorData)
            },
        })
        
    })

    function refreshCart(){
        console.log("in current cart")
        var cartTable = $(".cart-table")
        var cartBody = cartTable.find(".cart-body")
        var cartProductsRow = cartTable.find(".cart-products")
        var currentUrl = window.location.href
        var refreshCartUrl = 'api/cart'
        var refreshCartMethod = "GET"
        var data = {}
        $.ajax({
            url: refreshCartUrl,
            method: refreshCartMethod,
            data: data,
            success: function(data){
                console.log("success")
                var hiddenCartItemRemoveForm = $(".cart-item-remove-form")
                if (data.products.length > 0) {
                    cartProductsRow.html("")
                    i = data.products.length
                    $.each(data.products, function(index, value){
                        var newCartItemRemove = hiddenCartItemRemoveForm.clone()
                        newCartItemRemove.css("display", "block")
                        newCartItemRemove.find(".cart-item-product-id").val(value.id)
                        cartBody.prepend("<tr><th scope='row'>" + i + "</th><td><a href='" + value.url + "'>" + value.name + "</a>" + newCartItemRemove.html() + "</td><td>" + value.price + "</td></tr>")
                        i --
                    })
                    cartBody.find(".cart-subtotal").text(data.subtotal)
                    cartBody.find(".cart-total").text(data.total)
                } else {
                    window.location.href = currentUrl
                }
            },
            error: function(errorData){
                $.alert({
                    icon: 'fa fa-warning',
                    title: "Oops!",
                    content:"We couldn't update your cart.  Please try again",
                    type: 'orange',
                    typeAnimated: false,
                })
                console.log("error")
                console.log(errorData)
            },
        })
    }
})