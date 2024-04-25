$(document).ready(function(){
    var stripeFormModule = $('.stripe-payment-form')
    var stripeModuleToken = stripeFormModule.attr('data-token')
    var stripeModuleNextUrl = stripeFormModule.attr('data-next-url')
    var stripeModuleBtnTitle = stripeFormModule.attr('data-btn-title') || "Add Card"

    var stripeTemplate = $.templates('#stripeTemplate')
    var stripeTemplateContextData = {
        publishKey: stripeModuleToken,
        nextUrl: stripeModuleNextUrl,
        btnTitle: stripeModuleBtnTitle,
    }

    var stripeTemplateHtml = stripeTemplate.render(stripeTemplateContextData)

    stripeFormModule.html(stripeTemplateHtml)

    var paymentForm = $(".payment-form")
    if (paymentForm.length > 1){
        alert("only one payment form is allowed")
        paymentForm.css('display', 'none')
    }
    else if (paymentForm.length == 1){
        var pubKey = paymentForm.attr('data-token')
        var nextUrl = paymentForm.attr('data-next-url')
    }

    var stripe = Stripe(pubKey);
    var elements = stripe.elements()

    var style = {
        base: {
            color: "#32325d",
            lineHeight: "24px",
            fontFamily: '"Helvetica Neue", Helvetica, sans-seriff',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': {
                color: '#aab7c4'
            }
        },
        invalid: {
            color: '#fa755a',
            iconColor: '#fa755a',
        }
    };

    //create an instance of the card Element
    var card = elements.create('card', {style: style});

    // add an instance of the card Element into the card-element <div>
    card.mount('#card-element');

    // handle real time validation errors from the card element
    card.addEventListener('change', function(event) {
        var displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    });

    // handle form submission
    // var form = document.getElementById('payment-form');
    // form.addEventListener('submit', function(event) {
    //     event.preventDefault();

    //     var loadTime = 1500
    //     var errorHmtl = "<i class='fa fa-warning'></i> An error occured"
    //     var errorClasses = "btn btn-danger disabled"
    //     var loadingHmtl = "<i class='fa fa-spin fa-spinner'></i> Loading..."
    //     var loadingClasses = "btn btn-success disabled"
    //     stripe.createToken(card).then(function(result) {
    //         if (result.error) {
    //             //inform the user if error
    //             var errorElement = document.getElementById('card-errors');
    //             errorElement.textContent = result.error.message;
    //         } else {
    //             // send the token to your server
    //             stripeTokenHandler(nextUrl, result.token);
    //         }
    //     });
    // });

    var form = $('#payment-form');
    var btnLoad = form.find(".btn-loader")
    var btnLoadDefaultHtml = btnLoad.html()
    var btnLoadDefaultClasses = btnLoad.attr("class")

    form.on('submit', function(event) {
        event.preventDefault();

        var $this = $(this)
        btnLoad.blur()
        var loadTime = 1500
        var currentTimeout;
        var errorHmtl = "<i class='fa fa-warning'></i> An error occured"
        var errorClasses = "btn btn-danger disabled"
        var loadingHmtl = "<i class='fa fa-spin fa-spinner'></i> Loading..."
        var loadingClasses = "btn btn-success disabled"
        stripe.createToken(card).then(function(result) {
            if (result.error) {
                //inform the user if error
                var errorElement = $('#card-errors');
                    errorElement.textContent = result.error.message;
                    currentTimeout = displayBtnStatus(
                        btnLoad, 
                        errorHmtl, 
                        errorClasses, 
                        1000, 
                        currentTimeout,
                    )
            } else {
                currentTimeout = displayBtnStatus(
                        btnLoad, 
                        loadingHmtl, 
                        loadingClasses, 
                        2000, 
                        currentTimeout,
                    )
                // send the token to your server
                stripeTokenHandler(nextUrl, result.token);
            }
        });
    });

    function displayBtnStatus(element, newHtml, newClasses, loadTime, timeout){
        // if (timeout){
        //     clearTimeout(timeout)
        // }
        if (!loadTime){
            loadTime = 1500
        }
        element.html(newHtml)
        element.removeClass(btnLoadDefaultClasses)
        element.addClass(newClasses)
        return setTimeout(function(){
            element.html(btnLoadDefaultHtml)
            element.removeClass(newClasses)
            element.addClass(btnLoadDefaultClasses)
        }, loadTime)
    }

    function redirectToNext(nextPath, timeOffset){
        if (nextPath){
        setTimeout(function(){
            window.location.href = nextPath
        }, timeOffset)
        }
    }

    function stripeTokenHandler(nextUrl, token){
        console.log(nextUrl,token.id)
        var paymentMethodEndpoint = '/checkout/payment-create/'
        var data = {
            'token': token.id,
        }
        $.ajax({
            data: data,
            url: paymentMethodEndpoint,
            method: "POST",
            success: function(data){
                var successMsg = data.message || "Success! Card added"
                card.clear()
                if (nextUrl){
                    successMsg = successMsg + "<br/><i class='fa fa-spin fa-spinner'></i> Redirecting ..."
                } 
                if ($.alert){
                    $.alert(successMsg)
                } else {
                    alert(successMsg)
                }
                btnLoad.html(btnLoadDefaultHtml)
                btnLoad.attr("class", btnLoadDefaultClasses)
                redirectToNext(nextUrl, 1500)
                
                // else {
                    //     window.location.reload()
                    // }
                },
            error: function(error){
                $.alert({title: "An error occured", content: "Please try adding your card again."})
                btnLoad.html(btnLoadDefaultHtml)
                btnLoad.attr("class", btnLoadDefaultClasses)
                console.log(error)
            }
        })
    }
})