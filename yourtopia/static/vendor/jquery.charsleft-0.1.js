/** 
 * @projectDescription Characters Left Plug-in
 * @author 	Matt Hobbs (http://nooshu.com/)
 * @version 0.1
 * 
 * Plugin counts the number of characters a user has entered
 * in a textarea / input and adds a short paragraph reminding
 * the user.
 */
(function($){
	$.fn.charsLeft = function(customOptions){
		//Merge default and user options
		var options = $.extend({}, $.fn.charsLeft.defaultOptions, customOptions);
		return this.each(function(i){
			var $this = $(this);
			
			//Construct our HTML
			var charHTML = "<div class='" + options.wrapperClass + "'>";
			charHTML += options.charPrefix;
			charHTML += " <span class='" + options.countClass + "'>" + options.maxChars + "</span> ";
			charHTML += options.charSuffix;
			charHTML += "</div>";
			
			//Attach our HTML
			switch(options.attachment){
				case "before":
					$this.before(charHTML);
					break;
				case "after":
					$this.after(charHTML);
					break;
				default:
					$this.after(charHTML);
					break;
			}
			
			//Cache the char count
			$charCount = $("." + options.countClass);
			
			//Look at the length / what's left
			var messageLength = $this.attr("value").length;
			var messageCharsLeft = options.maxChars - messageLength;
			
			//On reload, if teaxtarea is filled, update value
			if(messageLength){
				$charCount.text(messageCharsLeft);
			}
			
			//Bind the update on textarea keyup
			$this.bind("keyup.charsLeft", function(){
				messageLength = $this.attr("value").length;
				messageCharsLeft = options.maxChars - messageLength;
				$charCount.text(messageCharsLeft);
				
				//Add error class if to many chars
				(messageCharsLeft < 0) ? $this.addClass(options.errorClass) : $this.removeClass(options.errorClass);
			});
		});
	};
	
	//Set our plugin defaults
	$.fn.charsLeft.defaultOptions = {
		maxChars: 140,
		charPrefix: "You have",
		charSuffix: "characters left.",
		attachment: "after",
		wrapperClass: "charsLeft",
		countClass: "charCount",
		errorClass: "charError"
	};
})(jQuery);