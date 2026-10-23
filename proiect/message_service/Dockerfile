FROM maven:3.8.8-eclipse-temurin-21 AS build
WORKDIR /app

ARG GITLAB_MAVEN_USER
ARG GITLAB_MAVEN_TOKEN

COPY pom.xml ./
COPY src ./src

RUN mkdir -p /root/.m2 && \
    printf '<?xml version="1.0" encoding="UTF-8"?><settings><servers><server><id>gitlab-maven</id><username>%s</username><password>%s</password></server></servers><mirrors><mirror><id>central-mirror</id><name>Central Mirror</name><url>https://repo.maven.apache.org/maven2</url><mirrorOf>central</mirrorOf></mirror></mirrors></settings>' "$GITLAB_MAVEN_USER" "$GITLAB_MAVEN_TOKEN" > /root/.m2/settings.xml

RUN mvn -U -B -s /root/.m2/settings.xml clean package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java","-jar","app.jar"]
