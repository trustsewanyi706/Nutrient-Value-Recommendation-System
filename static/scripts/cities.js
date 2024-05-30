var state_arr = new Array("Bulawayo", "Harare", "Manicaland", "Mashonaland Central", "Mashonaland East", "Mashonaland West", "Masvingo", "Matabeleland North", "Matabeleland South", "Midlands");

var s_a = new Array();
s_a[0] = "";
s_a[1] = "Bulawayo";
s_a[2] = "Harare | Chitungwiza | Norton";
s_a[3] = "Mutare | Chimanimani | Chipinge | Mutasa | Nyanga | Rusape";
s_a[4] = "Bindura | Centenary | Guruve | Mt. Darwin | Rushinga | Shamva | Mazowe";
s_a[5] = "Marondera | Goromonzi | Murehwa | Seke | Ruwa";
s_a[6] = "Chinhoyi | Kariba | Karoi | Makuti | Zvimba | Mutorashanga";
s_a[7] = "Masvingo | Bikita | Chiredzi | Chivi | Gutu | Masvingo | Zaka";
s_a[8] = "Hwange | Lupane | Victoria Falls";
s_a[9] = "Beitbridge | Gwanda | Insiza | Mangwe | Matobo";
s_a[10] = "Gweru | Gokwe | Kwekwe | Redcliff | Shurugwi | Zvishavane";



function print_state(state_id) {
    // given the id of the <select> tag as function argument, it inserts <option> tags
    var option_str = document.getElementById(state_id);
    option_str.length = 0;
    option_str.options[0] = new Option('Select Province', '');
    option_str.selectedIndex = 0;
    for (var i = 0; i < state_arr.length; i++) {
        option_str.options[option_str.length] = new Option(state_arr[i], state_arr[i]);
    }
}

function print_city(city_id, city_index) {
    var option_str = document.getElementById(city_id);
    option_str.length = 0; // Fixed by Julian Woods
    option_str.options[0] = new Option('Select City', '');
    option_str.selectedIndex = 0;
    var city_arr = s_a[city_index].split("|");
    for (var i = 0; i < city_arr.length; i++) {
        option_str.options[option_str.length] = new Option(city_arr[i], city_arr[i]);
    }
}

$(".hover").mouseleave(
    function() {
        $(this).removeClass("hover");
    }
);