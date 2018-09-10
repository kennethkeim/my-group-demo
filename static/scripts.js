// Code that executes on doc load....................................................................................................

// if on the home (events) page:
if (top.location.pathname === "/")
{
    // toggle active states on directory and event buttons
    var dirbtn = document.getElementById('dirbtn');
    var evbtn = document.getElementById('evbtn');
    evbtn.classList.add("active");
    dirbtn.classList.remove("active");

    // global variables to remember the id of last clicked event
    // the variable saves the database event id, and is passed in along with form data anytime an existing event is modified
    selected_ev_id = 0
    // url ready
    id_for_url = "id=0"


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
    location.href = "#";
    location.href = "#" + month_name;
}



// if on the directory page:
if (top.location.pathname === "/directory")
{

    // toggle active states on directory and event buttons
    var dirbtn = document.getElementById('dirbtn');
    var evbtn = document.getElementById('evbtn');
    dirbtn.classList.add("active");
    evbtn.classList.remove("active");

}




// Event handlers.............................................................................................................


// all events a tag click handler
$('a.allev_btn').on('click', function(e){
    e.preventDefault();
    selected_ev_id = $(this).attr('id');
    id_for_url = "id=" + selected_ev_id;
    return true;
});



// add event handler: initialize the modal with a blank form when 'add event' is clicked
// (this clears any data in the form that was prefilled if 'edit event' was clicked)
$('#addev_btn').on('click', function(){
    // assign empty values (these translate to 'None' type in python)
    var modal = $('#addev_modal');
    modal.find('.modal-title').text('Add New Event');
    modal.find('#title').val('');
    modal.find('#type').val('');
    modal.find('#month_num').val('');
    modal.find('#day_num').val('');
    modal.find('#time').val('');
    modal.find('#location').val('');
    modal.find('#notes').val('');
    modal.find('#hidden_event_id').val(0);

    // show the modal
    modal.modal({
        backdrop: 'static'
    },'show');
});




// edit event handler: prefill the modal form with all event info when 'edit event' is clicked
$('a.allev_btn').on('click', function(e){
    var thistag = $(this);
    $('#edit_pop_btn').on('click', function(){
        // get all the data for the selected event from the html elements
        var title = thistag.children('h6').text();
        var type = thistag.attr('name');
        var datetime = thistag.siblings().attr('datetime');
        var month_num = datetime[5] + datetime[6];
        var day_num = datetime[8] + datetime[9];
        var time = thistag.children('time').attr('datetime');
        var location = thistag.children('div').text();
        var notes = thistag.children('p').text();

        // initialize the 'edit event' form with the data
        var modal = $('#addev_modal');
        modal.find('.modal-title').text('Edit Event');
        modal.find('#title').val(title);
        modal.find('#type').val(type);
        modal.find('#month_num').val(month_num);
        modal.find('#day_num').val(day_num);
        modal.find('#time').val(time);
        modal.find('#location').val(location);
        modal.find('#notes').val(notes);
        modal.find('#hidden_event_id').val(selected_ev_id);

        // show the modal
        modal.modal({
        backdrop: 'static',
        },'show');
    });
});



// add/edit event form submission handler
$('#addev_form').on('submit', function(e){
     e.preventDefault();
     $('#addev_modal').modal('hide');
     $.ajax({
         url: "/addev",
         type: "POST",
         data: $( this ).serialize(),
         success: function(data){
             location.reload();
         },
         error: function(jqXHR, textStatus, errorThrown){
             $('#response').html("<p><div style='color: red;'>" + textStatus + " " + errorThrown + ": </div>" + jqXHR.responseText + "</p>");
             $('#response_modal').modal('show');
         }
     });
});



// delete event form submission handler
$('#del_confirm').on('click', function(){
     $.ajax({
         url: "/delev",
         type: "POST",
         data: id_for_url,
         success: function(){
             location.reload();
         },
         error: function(jqXHR, textStatus, errorThrown){
             $('#response').html("<p><div style='color: red;'>" + textStatus + " " + errorThrown + ": </div>" + jqXHR.responseText + "</p>");
             $('#response_modal').modal('show');
         }
     });
});
