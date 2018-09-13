

// toggle active states on directory and event buttons
var dirbtn = document.getElementById('dirbtn');
var evbtn = document.getElementById('evbtn');
dirbtn.classList.add("active");
evbtn.classList.remove("active");

// global variable to remember the id of last clicked contact
// the variable saves the contact's database id, and is passed in along with form data anytime an existing contact is modified
selected_contact_id = 0;


// initiate popups on all contacts a tags
var popupContent = '<button class="btn btn-sm" id="edit_pop_btn"><i class="fas fa-pencil-alt"></i> edit</button>' + '<button class="btn btn-sm" id="del_pop_btn" data-toggle="modal" data-target="#delcontact_modal" data-backdrop="static"><i class="fas fa-trash-alt"></i> delete</button>';

$(".popoverSelector").popover({
    animation: true,
    content: popupContent,
    placement: 'bottom',
    container: 'body',
    trigger: 'focus',
    html: true
});









// Event handlers.............................................................................................................



// all contacts a tag click handler
$('a.popoverSelector').on('click', function(e){
    e.preventDefault();
    selected_contact_id = $(this).attr('id');
});




// show the 'add contact' form
$('#addcontact_btn').on('click', function(){

   // reset all the values in the form
    $('#addcontact_form').trigger('reset');

    // show the modal
    $('#addcontact_modal').modal({backdrop: 'static'},'show');
});




// add contact form submission handler
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




// prefill the 'edit contact' form with all info for clicked contact
// show the edit contact form
// THIS IS A COPY OF THE WAY I DID IT LAST TIME AND PROBS NOT THE BEST WAY TO AVOID THE POPOVER PROBLEM
// I'm tired and don't have time to fix right now
$('a.popoverSelector').on('click', function(){
    $('#edit_pop_btn').on('click', function(){

       $.ajax({
          url: `/directory/${selected_contact_id}/edit`,
          type: "GET",
          success: function(data){
             contact = JSON.parse(data);

             // initialize the 'edit event' form with the data
             var modal = $('#editcontact_modal');
             modal.find('#firstNameEdit').val(contact.first_name);
             modal.find('#lastNameEdit').val(contact.last_name);
             modal.find('#phone0Edit').val(contact.phone0);
             modal.find('#phone1Edit').val(contact.phone1);
             modal.find('#addrLine0Edit').val(contact.addr_line1);
             modal.find('#addrLine1Edit').val(contact.addr_line2);
             modal.find('#cityEdit').val(contact.city);
             modal.find('#stateEdit').val(contact.state);
             modal.find('#postalEdit').val(contact.postal);

             // show the modal
             modal.modal({backdrop: 'static'},'show');
          },
          error: function(jqXHR, textStatus, errorThrown){
             $('h1').after(`<div id="error_message">${errorThrown}: ${jqXHR.responseText}</div>`);
          }
       });
    });
});





// edit contact form submission handler
$('#editcontact_form').on('submit', function(e){
     e.preventDefault();
     $('#editcontact_modal').modal('hide');

     $.ajax({
         url: `/directory/${selected_contact_id}`,
         type: "PUT",
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
