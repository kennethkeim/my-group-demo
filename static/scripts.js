// Code that executes on doc load....................................................................................................

// if on the home (events) page:
if (window.location.pathname.includes("events"))
{
    // toggle active states on directory and event buttons
    var dirbtn = document.getElementById('dirbtn');
    var evbtn = document.getElementById('evbtn');
    evbtn.classList.add("active");
    dirbtn.classList.remove("active");

    // activate the jQuery UI datepicker
    $('#datepicker1').datepicker();
    $('#datepicker2').datepicker();


    // global variable to remember the id of last clicked event
    // the variable saves the event's database id, and is passed in along with form data anytime an existing event is modified
    selected_ev_id = 0


    // initiate popups on all events a tags
    var popup_content = '<button class="btn btn-sm" id="edit_pop_btn"><i class="fas fa-pencil-alt"></i> edit</button>' + '<button class="btn btn-sm" id="del_pop_btn" data-toggle="modal" data-target="#del_modal" data-backdrop="static"><i class="fas fa-trash-alt"></i> delete</button>'

    $(".allev_btn").popover({
        animation: true,
        content: popup_content,
        placement: 'bottom',
        container: 'body',
        trigger: 'focus',
        html: true
    });

    // get the current date and scroll to the current month
    var months = ["","January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    var date = new Date();
    var month_name = months[date.getMonth() +1];
    window.location.href = "#" + month_name;

    // in case I need to scroll a given number of pixels
    // var pixels = $(window).scrollTop() - 60;
    // $(window).scrollTop(pixels);
}



// if on the directory page:
if (window.location.pathname == "/directory")
{
    // toggle active states on directory and event buttons
    var dirbtn = document.getElementById('dirbtn');
    var evbtn = document.getElementById('evbtn');
    dirbtn.classList.add("active");
    evbtn.classList.remove("active");

    // global variable to remember the id of last clicked contact
    // the variable saves the contact's database id, and is passed in along with form data anytime an existing contact is modified
    selected_contact_id = 0


    // initiate popups on all contacts a tags
    var popupContent = '<button class="btn btn-sm" id="edit_pop_btn"><i class="fas fa-pencil-alt"></i> edit</button>' + '<button class="btn btn-sm" id="del_pop_btn" data-toggle="modal" data-target="#delcontact_modal" data-backdrop="static"><i class="fas fa-trash-alt"></i> delete</button>'

    $(".popoverSelector").popover({
        animation: true,
        content: popupContent,
        placement: 'bottom',
        container: 'body',
        trigger: 'focus',
        html: true
    });
}




// Event handlers.............................................................................................................


// dismiss the navbar when a month is clicked in mobile
$('.mobile_nav_btn').click(function() {
   $('.navbar-toggler').trigger('click');
});


// all events a tag click handler
$('a.allev_btn').on('click', function(e){
    e.preventDefault();
    selected_ev_id = $(this).attr('id');
});

// all events a tag click handler
$('a.popoverSelector').on('click', function(e){
    e.preventDefault();
    selected_contact_id = $(this).attr('id');
});


// show the 'add event' form
$('#addev_btn').on('click', function(){

   // reset all the values in the form
    $('#addev_form').trigger('reset');

    // show the modal
    $('#addev_modal').modal({backdrop: 'static'},'show');
});



// prefill the 'edit event' form with all event info for clicked event
// show the edit event form
$('a.allev_btn').on('click', function(){
    var thistag = $(this);
    $('#edit_pop_btn').on('click', function(){
        // get all the data for the selected event from the html elements
        var title = thistag.children('h6').text();
        var type = thistag.attr('name');
        var date = thistag.siblings().attr('datetime');
        var formattedDate = `${date.substring(5, 7)}/${date.substring(8)}/${date.substring(0,4)}`;
        var time = thistag.children('time').attr('datetime');
        var location = thistag.children('div').text();
        var notes = thistag.children('p').text();

        // initialize the 'edit event' form with the data
        var modal = $('#editev_modal');
        modal.find('#title2').val(title);
        modal.find('#type2').val(type);
        modal.find('#datepicker2').val(formattedDate)
        modal.find('#time2').val(time);
        modal.find('#location2').val(location);
        modal.find('#notes2').val(notes);

        // show the modal
        modal.modal({backdrop: 'static'},'show');
    });
});




// add event form submission handler
$('#addev_form').on('submit', function(e){
     e.preventDefault();
     $('#addev_modal').modal('hide');

     $.ajax({
         url: '/events',
         type: "POST",
         data: $( this ).serialize(),
         success: function(){
             location.reload();
         },
         error: function(jqXHR, textStatus, errorThrown){
             $('#response').html("<p><div style='color: red;'>" + textStatus + " " + errorThrown + ": </div>" + jqXHR.responseText + "</p>");
             $('#response_modal').modal('show');
         }
     });
});


// edit event form submission handler
$('#editev_form').on('submit', function(e){
     e.preventDefault();
     $('#editev_modal').modal('hide');

     $.ajax({
         url: `/events/${selected_ev_id}`,
         type: "PUT",
         data: $( this ).serialize(),
         success: function(){
             location.reload();
         },
         error: function(jqXHR, textStatus, errorThrown){
             $('#response').html("<p><div style='color: red;'>" + textStatus + " " + errorThrown + ": </div>" + jqXHR.responseText + "</p>");
             $('#response_modal').modal('show');
         }
     });
});



// delete event form submission handler
$('#delev_confirm').on('click', function(){
     $.ajax({
         url: `/events/${selected_ev_id}`,
         type: "DELETE",
         success: function(){
             location.reload();
         },
         error: function(jqXHR, textStatus, errorThrown){
             $('#response').html("<p><div style='color: red;'>" + textStatus + " " + errorThrown + ": </div>" + jqXHR.responseText + "</p>");
             $('#response_modal').modal('show');
         }
     });
});



// import events to new year form submission handler
$('#importev_form').on('submit', function(e){
     e.preventDefault();

     $.ajax({
         url: '/admin/importevents',
         type: "POST",
         data: $( this ).serialize(),
         success: function(data){
             $('#importev_form').trigger('reset');
             $('#col').append(`<div id="success_message">${data}</div>`);
         },
         error: function(jqXHR, textStatus, errorThrown){
            $('#col').append(`<div id="error_message">${errorThrown}: ${jqXHR.responseText}</div>`);
         }
     });
});



// show the 'add contact' form
$('#addcontact_btn').on('click', function(){

   // reset all the values in the form
    $('#addcontact_form').trigger('reset');

    // show the modal
    $('#addcontact_modal').modal({backdrop: 'static'},'show');
});


// add event form submission handler
$('#addcontact_form').on('submit', function(e){
     e.preventDefault();
     $('#addcontact_modal').modal('hide');

     $.ajax({
         url: '/directory',
         type: "POST",
         data: $( this ).serialize(),
         success: function(){
             location.reload();
         },
         error: function(jqXHR, textStatus, errorThrown){
            $('h1').after(`<div id="error_message">${errorThrown}: ${jqXHR.responseText}</div>`);
         }
     });
});




// delete contact form submission handler
$('#delcontact_confirm').on('click', function(){
     $.ajax({
         url: `/directory/${selected_contact_id}`,
         type: "DELETE",
         success: function(){
             location.reload();
         },
         error: function(jqXHR, textStatus, errorThrown){
            $('h1').after(`<div id="error_message">${errorThrown}: ${jqXHR.responseText}</div>`);
         }
     });
});
