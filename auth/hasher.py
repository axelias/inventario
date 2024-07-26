from streamlit_authenticator.utilities.hasher import Hasher

# Pass the list of passwords directly to the 
# Hasher constructor and generate the hashes
passwords_to_hash = ['inv247']
hashed_passwords = Hasher(passwords_to_hash).generate()

print(hashed_passwords)