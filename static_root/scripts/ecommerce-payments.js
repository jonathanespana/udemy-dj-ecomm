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
    var form = document.getElementById('payment-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        stripe.createToken(card).then(function(result) {
            if (result.error) {
                //inform the user if error
                var errorElement = document.getElementById('card-errors');
                errorElement.textContent = result.error.message;
            } else {
                // send the token to your server
                stripeTokenHandler(nextUrl, result.token);
            }
        });
    });

    function redirectToNext(nextPath, timeOffset){
        if (nextPath){
        setTimeout(function(){
            window.location.href = nextPath
        }, timeOffset)
        }
    }

    function stripeTokenHandler(nextUrl, token){
        console.log(nextUrl,token.id)
        var paymentMethodEndpoint = '/checkout/payment-create'
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
                redirectToNext(nextUrl, 1500)

                // else {
                //     window.location.reload()
                // }
            },
            error: function(error){
                console.log(error)
            }
        })
    }
})