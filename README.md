# Petit_RAG

a simple project to create a light small RAG application

This project behavior is to copy your selected file into a local folder which will be used as sources for the Retrievement Augmented Generation.
A simple vector database will save the vectorial representation of the chunk, it's source file, it's index of it's first character in the raw documents and it's length (e.g 512 character)
When there is a prompt we get the chunks index and the file needed and we retrieve it directly from the document,
if there is padding an algorithme will make the union of the index to reduce redonancy.
for exemple if we have chunk_1 (first index = 0, length 512) and chunk_2 (first index = 256, length 512) we will only get a chunk from index 0 to 768

# TODO

- [ ] Fastapi base (i.e endpoints pydantic models).
- [ ] Web interface (prompt form, add/delete file buttons) in html/css/js.
- [ ] Files parser (txt/md, pdf) in python
- [ ] Database collection with sqlite3 + sqlite_vec
- [ ] Language Model anwser generation with python llama_cpp
