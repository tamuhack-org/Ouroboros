-- If application_application ever gets dropped, run this file to recreate it
-- BUT if there have been other migrations since 0017, you'll have to run those afterward (or just append them to this file)


-- 0001
BEGIN;
CREATE TABLE "application_application" ("id" uuid NOT NULL PRIMARY KEY, "datetime_submitted" timestamp with time zone NOT NULL, "status" varchar(1) NOT NULL, "first_name" varchar(255) NOT NULL, "last_name" varchar(255) NOT NULL, "extra_links" varchar(200) NOT NULL, "question1" text NOT NULL, "question2" text NOT NULL, "question3" text NOT NULL, "resume" varchar(100) NOT NULL, "major" varchar(255) NOT NULL, "classification" varchar(3) NOT NULL, "gender" varchar(2) NOT NULL, "gender_other" varchar(255) NULL, "race" varchar(41) NOT NULL, "race_other" varchar(255) NULL, "grad_year" integer NOT NULL, "num_hackathons_attended" varchar(22) NOT NULL, "agree_to_coc" boolean NOT NULL, "is_adult" boolean NOT NULL, "shirt_size" varchar(4) NOT NULL, "transport_needed" varchar(11) NOT NULL, "travel_reimbursement" boolean NOT NULL, "additional_accommodations" text NOT NULL, "dietary_restrictions" varchar(50) NOT NULL, "confirmation_deadline" timestamp with time zone NULL, "notes" text NOT NULL, "school_id" integer NULL);
ALTER TABLE "application_application" ADD CONSTRAINT "application_applicat_school_id_18ad9b79_fk_applicati" FOREIGN KEY ("school_id") REFERENCES "application_school" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "application_application_school_id_18ad9b79" ON "application_application"("school_id");
COMMIT;


-- 0002
BEGIN;
--
-- Add field user to application
--
ALTER TABLE "application_application" ADD COLUMN "user_id" integer NOT NULL;
--
-- Add field wave to application
--
ALTER TABLE "application_application" ADD COLUMN "wave_id" integer NOT NULL;
CREATE INDEX "application_application_user_id_4a508f9e" ON "application_application" ("user_id");
ALTER TABLE "application_application" ADD CONSTRAINT "application_application_user_id_4a508f9e_fk_user_user_id" FOREIGN KEY ("user_id") REFERENCES "user_user" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "application_application_wave_id_7a74772a" ON "application_application" ("wave_id");
ALTER TABLE "application_application" ADD CONSTRAINT "application_application_wave_id_7a74772a_fk_application_wave_id" FOREIGN KEY ("wave_id") REFERENCES "application_wave" ("id") DEFERRABLE INITIALLY DEFERRED;
COMMIT;


-- 0003
BEGIN;
--
-- Add field school_other to application
--
ALTER TABLE "application_application" ADD COLUMN "school_other" varchar(255) NULL;
COMMIT;


-- 0005
BEGIN;
--
-- Add field dietary_restrictions_other to application
--
ALTER TABLE "application_application" ADD COLUMN "dietary_restrictions_other" varchar(255) NULL;
--
-- Remove field dietary_restrictions from application
--
ALTER TABLE "application_application" DROP COLUMN "dietary_restrictions" CASCADE;


-- 0008
BEGIN;
--
-- Add field hackathon_purpose to application
--
ALTER TABLE "application_application" ADD COLUMN "hackathon_purpose" varchar(16) DEFAULT 'R' NOT NULL;
ALTER TABLE "application_application" ALTER COLUMN "hackathon_purpose" DROP DEFAULT;
--
-- Add field has_team to application
--
ALTER TABLE "application_application" ADD COLUMN "has_team" boolean DEFAULT true NOT NULL;
ALTER TABLE "application_application" ALTER COLUMN "has_team" DROP DEFAULT;
--
-- Add field wants_team to application
--
ALTER TABLE "application_application" ADD COLUMN "wants_team" boolean DEFAULT false NOT NULL;
ALTER TABLE "application_application" ALTER COLUMN "wants_team" DROP DEFAULT;

COMMIT;


-- 0009
BEGIN;
--
-- Add field technology_experience to application
--
ALTER TABLE "application_application" ADD COLUMN "technology_experience" varchar(150) NOT NULL;
COMMIT;


-- 0010
BEGIN;
--
-- Alter field hackathon_purpose on application
--
--
-- Alter field has_team on application
--
ALTER TABLE "application_application" ALTER COLUMN "has_team" TYPE varchar(16) USING "has_team"::varchar(16);
--
-- Alter field wants_team on application
--
ALTER TABLE "application_application" ALTER COLUMN "wants_team" TYPE varchar(16) USING "wants_team"::varchar(16);
COMMIT;


-- 0011
BEGIN;
-- Remove field dietary_restrictions_other from application
--
ALTER TABLE "application_application" DROP COLUMN "dietary_restrictions_other" CASCADE;
--
-- Remove field hackathon_purpose from application
--
ALTER TABLE "application_application" DROP COLUMN "hackathon_purpose" CASCADE;
--
-- Remove field transport_needed from application
--
ALTER TABLE "application_application" DROP COLUMN "transport_needed" CASCADE;
--
-- Remove field travel_reimbursement from application
--
ALTER TABLE "application_application" DROP COLUMN "travel_reimbursement" CASCADE;
--
-- Add field address to application
--
ALTER TABLE "application_application" ADD COLUMN "address_id" integer NOT NULL;
--
-- Alter field wants_team on application
--
CREATE INDEX "application_application_address_id_3434c2a4" ON "application_application" ("address_id");
ALTER TABLE "application_application" ADD CONSTRAINT "application_applicat_address_id_3434c2a4_fk_address_a" FOREIGN KEY ("address_id") REFERENCES "address_address" ("id") DEFERRABLE INITIALLY DEFERRED;
COMMIT;


-- 0012
BEGIN;
--
-- Alter field address on application
--
SET CONSTRAINTS "application_applicat_address_id_3434c2a4_fk_address_a" IMMEDIATE; ALTER TABLE "application_application" DROP CONSTRAINT "application_applicat_address_id_3434c2a4_fk_address_a";
ALTER TABLE "application_application" ADD CONSTRAINT "application_applicat_address_id_3434c2a4_fk_address_a" FOREIGN KEY ("address_id") REFERENCES "address_address" ("id") DEFERRABLE INITIALLY DEFERRED;
COMMIT;


-- 0014
BEGIN;
--
-- Add field agree_to_mlh_stuff to application
--
ALTER TABLE "application_application" ADD COLUMN "agree_to_mlh_stuff" boolean NULL;
--
-- Alter field address on application
--
SET CONSTRAINTS "application_applicat_address_id_3434c2a4_fk_address_a" IMMEDIATE; ALTER TABLE "application_application" DROP CONSTRAINT "application_applicat_address_id_3434c2a4_fk_address_a";
ALTER TABLE "application_application" ALTER COLUMN "address_id" DROP NOT NULL;
ALTER TABLE "application_application" ADD CONSTRAINT "application_applicat_address_id_3434c2a4_fk_address_a" FOREIGN KEY ("address_id") REFERENCES "address_address" ("id") DEFERRABLE INITIALLY DEFERRED;
--
-- Alter field wants_team on application
--
COMMIT;


-- 0015
BEGIN;
--
-- Alter field technology_experience on application
--
ALTER TABLE "application_application" ALTER COLUMN "technology_experience" TYPE varchar(450) USING "technology_experience"::varchar(450);
COMMIT;


-- 0017
BEGIN;
--
-- Remove field address from application
--
SET CONSTRAINTS "application_applicat_address_id_3434c2a4_fk_address_a" IMMEDIATE; ALTER TABLE "application_application" DROP CONSTRAINT "application_applicat_address_id_3434c2a4_fk_address_a";
ALTER TABLE "application_application" DROP COLUMN "address_id" CASCADE;
--
-- Remove field question2 from application
--
ALTER TABLE "application_application" DROP COLUMN "question2" CASCADE;
--
-- Remove field question3 from application
--
ALTER TABLE "application_application" DROP COLUMN "question3" CASCADE;
--
-- Add field dietary_restrictions to application
--
ALTER TABLE "application_application" ADD COLUMN "dietary_restrictions" varchar(5000) NOT NULL;
--
-- Alter field additional_accommodations on application
--
--
-- Alter field grad_year on application
--
--
-- Alter field question1 on application
--
--
-- Alter field technology_experience on application
--
ALTER TABLE "application_application" ALTER COLUMN "technology_experience" TYPE varchar(5000) USING "technology_experience"::varchar(5000);
--
-- Alter field wants_team on application
--
COMMIT;


-- 0018

BEGIN;
--
-- Add field emergency_contact_email to application
--
ALTER TABLE "application_application" ADD COLUMN "emergency_contact_email" varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE "application_application" ALTER COLUMN "emergency_contact_email" DROP DEFAULT;
--
-- Add field emergency_contact_name to application
--
ALTER TABLE "application_application" ADD COLUMN "emergency_contact_name" varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE "application_application" ALTER COLUMN "emergency_contact_name" DROP DEFAULT;
--
-- Add field emergency_contact_phone to application
--
ALTER TABLE "application_application" ADD COLUMN "emergency_contact_phone" varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE "application_application" ALTER COLUMN "emergency_contact_phone" DROP DEFAULT;
--
-- Add field emergency_contact_relationship to application
--
ALTER TABLE "application_application" ADD COLUMN "emergency_contact_relationship" varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE "application_application" ALTER COLUMN "emergency_contact_relationship" DROP DEFAULT;
--
-- Alter field num_hackathons_attended on application
--
--
-- Alter field race on application
--
--
-- Alter field wants_team on application
--
COMMIT;


-- 0019
BEGIN;
--
-- Alter field emergency_contact_email on application
--
--
-- Alter field emergency_contact_name on application
--
--
-- Alter field emergency_contact_phone on application
--
--
-- Alter field emergency_contact_relationship on application
--
-- Add field wares on application
ALTER TABLE "application_application" ADD COLUMN "wares" varchar(5000) DEFAULT '' NOT NULL;
ALTER TABLE "application_application" ALTER COLUMN "wares" DROP DEFAULT;
COMMIT;

