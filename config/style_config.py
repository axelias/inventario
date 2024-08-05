css_style = """

<style>
    iframe:first-of-type{
        margin-top: -11.5rem;
    }
    button[data-testid="baseButton-primary"]{
        background-color: #f0f2f6;
        border: 1px solid green;
        color: black;
    }
    button[data-testid="baseButton-primary"]:hover{
        background-color: green;
        color: white;
        border: none;
    }

    button[data-testid="baseButton-secondary"]{
        background-color: #f0f2f6;
        border: 1px solid #d92232;
        color: black;
    }
    button[data-testid="baseButton-secondary"]:hover{
        background-color: #d92232;
        color: white;
        border: none;
    }

    iframe[title="streamlit_option_menu.option_menu"] {
        width: 60%;
        padding-left: 20%;
        margin-left: 10%;
    }

    @media(max-width:640px) {
        iframe:first-of-type{
            margin-top: -13.5rem;
            margin-left: 0rem;
            margin-right: 0rem;
            width: 85%;
        }

        iframe[title="streamlit_option_menu.option_menu"]{
            width: 100%;
            padding-left: 0px;
            margin-left: 0px;
        }
        
    }
</style>

"""