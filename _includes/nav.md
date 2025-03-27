<!-- Navbar -->
<div class="w3-to w3-white" style="border-bottom: 2px solid #f5f5f5;">
  <div class="w3-bar w3-content w3-white w3-left-align w3-large" style="max-width: 1100px; padding: 8px 0px;">
    <button  onclick="myFunction2('navDemo')" class="w3-bar-item w3-button w3-hide-medium w3-hide-large w3-right w3-large w3-white" title="Toggle Navigation Menu">
    <svg width="30px" height="30px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M8 12H8.00901M12.0045 12H12.0135M15.991 12H16" stroke="#484848" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="12" cy="12" r="10" stroke="#484848" stroke-width="1.5"/>
</svg>
    </button>
    <a href="{{ site.url }}" class="w3-bar-item w3-button w3-padding-larg"><b class="w3-text-dark-gray">
        <img src="{{ site.url }}/images/logo.png" alt="Logo" height="34px">
        Whatsapp Group Link</b></a>
    
   
      <div class="w3-dropdown-hover w3-bar-item w3-hide-small" style="margin-top:3px;">
        <button class="w3-button w3-small">Explore Groups</button>
        <div class="w3-dropdown-content w3-bar-block w3-white w3-border w3-border-light-gray w3-padding" style="border-radius: 15px;">
         <div class="w3-row">
        {% for post in site.categories.Group-Links %}
    {% if post.url %}
        <a class="w3-small" href="{{ post.url }}">{{ post.title }}</a></li>
    <hr style="margin:0px; margin:3px 0px;">
    {% endif %}
  {% endfor %}
        </div>
         
        
        </div>
      </div>
   <div class="w3-dropdown-hover w3-bar-item w3-hide-small" style="margin-top:3px;">
        <button class="w3-button w3-small">Posts</button>
        <div class="w3-dropdown-content w3-bar-block w3-white w3-border w3-border-light-gray w3-padding" style="border-radius: 15px;">
         <div class="w3-row">
        {% for post in site.categories.Posts %}
    {% if post.url %}
        <a class="w3-small" href="{{ post.url }}">{{ post.title }}</a></li>
    <hr>
    {% endif %}
  {% endfor %}
        </div>
         
        
        </div>
      </div>
    
    <a href="{{ site.url }}/about-us.html" class="w3-bar-item w3-button w3-hide-small w3-padding-large w3-hover-white w3-small" style="margin-top:6px;">About Us</a>
    <a href="{{ site.url }}/contact-us.html" class="w3-bar-item w3-button w3-hide-small w3-padding-large w3-hover-white w3-small" style="margin-top:6px;">Contact Us</a>
   
    
  <a href="{{ site.url }}/submit.html" class="w3-bar-item w3-button w3-hide-small w3-padding-large w3-hover-white w3-small" style="margin-top:6px;">Submit Group</a>
  </div>

  <!-- Navbar on small screens -->
  <div id="navDemo" class="w3-bar-block w3-hide-large w3-hide-medium w3-large w3-hide" style="background-color: #f6f6f6; border-top: 2px solid #f5f5f5;">
    <a href="{{ site.url }}" class="w3-bar-item w3-button w3-padding-large">Home</a>

 

<button onclick="myFunction2('menu3')" class="w3-border-top w3-border-white w3-bar-item w3-button w3-padding-large w3-left-align">Explore Groups</button>
<div id="menu3" class="w3-container w3-white w3-hide">
          
     {% for post in site.categories.Group-Links %}
    {% if post.url %}
        <a class="w3-large w3-row" style="padding:3px 18px;" href="{{ post.url }}">{{ post.title }}</a>
        
    {% endif %}
  {% endfor %}
         
</div>

<button onclick="myFunction2('menu4')" class="w3-border-top w3-border-white w3-bar-item w3-button w3-padding-large w3-left-align">Explore Posts</button>
<div id="menu4" class="w3-container w3-white w3-hide">
          
     {% for post in site.categories.Posts %}
    {% if post.url %}
        <a class="w3-large w3-row" style="padding:3px 18px;" href="{{ post.url }}">{{ post.title }}</a>
        
    {% endif %}
  {% endfor %}
         
</div>

    <a href="{{ site.url }}/about-us.html" class="w3-border-top w3-border-white w3-bar-item w3-button w3-padding-large">About Us</a>
    <a href="{{ site.url }}/contact-us.html" class="w3-border-top w3-border-white w3-bar-item w3-button w3-padding-large">Contact Us</a>
    <a href="{{ site.url }}/privacy-policy.html" class="w3-border-top w3-border-white w3-bar-item w3-button w3-padding-large">Privacy Policy</a>
    <a href="{{ site.url }}/disclaimer.html" class="w3-border-top w3-border-white w3-bar-item w3-button w3-padding-large">Disclaimer</a>
     <a href="{{ site.url }}/submit.html" class="w3-border-top w3-border-white w3-bar-item w3-button w3-padding-large">Submit Group</a>
  </div>
</div>