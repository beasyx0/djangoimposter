/*add or remove text inputs on click

submit form
create post django view
return post id on success
redirect to post detail page 

	<input type="text" name="testing">
		<input type="text" name="testing">
		<a class="submit">submit</a> */

<script>
	var formData = new FormData();

	$(document).on('click', '.submit', function(e) {
		formData.append('title', $('#id_title').val())
  		formData.append('author', $('#id_author').val())
  		formData.append('overview', $('#id_overview').val())
  		formData.append('content', $('#id_content').val())
  		formData.append('tags', $('#id_tag_str').val())
  		formData.append('previous_post_id', $('#id_previous_post').val())
  		formData.append('next_post_id', $('#id_next_post').val())
  		formData.append('image',  $('#id_post_image')[0].files[0])
  		formData.append('featured', $('#id_featured').val())
    	formData.append('csrfmiddlewaretoken', '{{ csrf_token }}')
      	$.ajax({
			type: 'POST',
			url: '{% url "blog:create-post-test" %}',
			data: formData,
			cache: false,
			processData: false,
			contentType: false,
			enctype: 'multipart/form-data',
			success: function (response){
				var postSlug = response.post_slug;	
				window.location.replace('http://127.0.0.1:8000/posts/'+response.post_slug);
			},
			error: function(xhr, errmsg, err) {
				console.log(xhr.status + ":" + xhr.responseText)
			},
		});
  	});
</script>

<script>  
	function onClick(event) {
	  var tags_str = $('input[name^=testing]').map(function(idx, elem) {
	    return $(elem).val();
	  }).get();

	  alert(tags_str)
	  event.preventDefault();
	}

	$(function() {
	  $('.submit').click(onClick);
	});
</script>


		/* <div class="tag-input-container"></div>
		<a href="#" id="add-tag-input">add tag</a> | 
		<a href="#" id="remove-tag-input">remove tag</a> */
	<script>
		$('#add-tag-input').click(function(event){
			event.preventDefault();
			$('.tag-input-container').append('<div><input type="text" id="tags" class="mb-2"></div>');
		});
	</script>
	<script>
		$('#remove-tag-input').click(function(event){
			event.preventDefault();
			$('.tag-input-container').children().last().remove();
		});
	</script>