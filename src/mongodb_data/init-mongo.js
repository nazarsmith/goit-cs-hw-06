db = db.getSiblingDB('test_db');

db.createUser({
  user: "db_user",
  pwd: "12341234",
  roles: [
    {
      role: "readWrite",
      db: "test_db"
    }
  ]
});

db.createCollection("homework_project");