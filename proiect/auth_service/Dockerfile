# Build stage
FROM maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /app

ARG GITLAB_MAVEN_USER
ARG GITLAB_MAVEN_TOKEN

COPY pom.xml .
COPY src ./src

RUN mkdir -p /root/.m2 && \
    printf '<settings><servers><server><id>gitlab-maven</id><username>%s</username><password>%s</password></server></servers></settings>' "$GITLAB_MAVEN_USER" "$GITLAB_MAVEN_TOKEN" > /root/.m2/settings.xml

RUN mvn -U -B -s /root/.m2/settings.xml dependency:go-offline
RUN mvn -U -B -s /root/.m2/settings.xml clean package -DskipTests

# Runtime stage
FROM eclipse-temurin:21-jre
WORKDIR /app

COPY --from=build /app/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]