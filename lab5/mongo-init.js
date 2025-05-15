db = db.getSiblingDB('library_db');

db.createUser({
  user: 'mongo_admin',
  pwd: 'password',
  roles: [
    {
      role: 'readWrite',
      db: 'library_db'
    }
  ]
});

db.createCollection('books');

db.books.createIndex({ "title": 1 });
db.books.createIndex({ "author": 1 });
db.books.createIndex({ "created_at": 1 });

print("MongoDB ініціалізація для library_db завершена :D");